import os
import logging
import tempfile
import subprocess
from contextlib import contextmanager
from functools import partial
from abc import abstractmethod as abstract

from .. import lekvar
from ..errors import *

from . import bindings as llvm

def emit(module:lekvar.Module, logger = logging.getLogger()):
    State.logger = logger.getChild("llvm")
    llvm.State.logger = State.logger.getChild("bindings")

    with State.begin("main", logger):
        module.emit()

    try:
        State.module.verify()
    except llvm.VerificationError as e:
        State.logger.error(e)

    return State.module.toString()

def run(source:bytes):
    try:
        return subprocess.check_output("lli",
            input = source,
            stderr = subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as e:
        raise ExecutionError(e.output)

class State:
    @classmethod
    @contextmanager
    def begin(cls, name:str, logger:logging.Logger):
        cls.logger = logger

        cls.self = None
        cls.builder = llvm.Builder.new()
        cls.module = llvm.Module.fromName(name)

        main_type = llvm.Function.new(llvm.Int.new(32), [], False)
        cls.main = cls.module.addFunction("main", main_type)
        cls.main.appendBlock("entry")
        main_exit = cls.main.appendBlock("exit")

        yield

        # add a goto exit for the last block
        with cls.blockScope(cls.main.getLastBlock().getPrevious()):
            State.builder.br(main_exit)

        with cls.blockScope(main_exit):
            return_value = llvm.Value.constInt(llvm.Int.new(32), 0, False)
            cls.builder.ret(return_value)

    @classmethod
    def addMainInstructions(cls, instructions:[lekvar.Object]):
        last_block = cls.main.getLastBlock().getPrevious()
        with cls.blockScope(last_block):
            for instruction in instructions:
                instruction.emitValue()

    @classmethod
    @contextmanager
    def blockScope(cls, block:llvm.Block):
        previous_block = cls.builder.position
        cls.builder.positionAtEnd(block)
        yield
        cls.builder.positionAtEnd(previous_block)

    @classmethod
    @contextmanager
    def selfScope(cls, self:llvm.Value):
        previous_self = cls.self
        cls.self = self
        yield
        cls.self = previous_self

    @classmethod
    def getTempName(self):
        return "temp"

    # Emmit an allocation as an instruction
    # Enforces allocation to happen early
    @classmethod
    def alloca(cls, type:llvm.Type, name:str):
        # Find first block
        entry = cls.builder.position.function.getFirstBlock()

        with cls.blockScope(entry):
            cls.builder.positionAt(entry, entry.firstValue)
            value = cls.builder.alloca(type, name)
        return value

    # Get a value which is a pointer to a value
    # Requires an allocation
    @classmethod
    def pointer(cls, value):
        variable = State.alloca(value.type, State.getTempName())
        State.builder.store(value, variable)
        return variable

# Abstract extensions

lekvar.BoundObject.llvm_value = None
lekvar.Function.llvm_return = None

# Extension abstract methods apparently don't work
#@abstract
#def Object_emitValue(self, state:State) -> llvm.Value:
#    pass
#lekvar.Object.emitValue = Object_emitValue

#@abstract
#def Type_emitType(self, state:State) -> llvm.Type:
#    pass
#lekvar.Type.emitType = Type_emitType
#lekvar.Type.llvm_type = None

def Object_emitContext(self):
    return None
lekvar.Object.emitContext = Object_emitContext

#
# Tools
#

def resolveName(scope:lekvar.BoundObject):
    # Resolves the name of a scope, starting with a extraneous .
    name = ""
    while scope.bound_context is not None:
        name = "." + scope.name + name
        scope = scope.bound_context.scope
    return "lekvar" + name

# Implements

# For this that don't emit anything
def blank_emitValue(self):
    return None
lekvar.Comment.emitValue = blank_emitValue

#
# class Reference
#

def Reference_emit(self):
    return self.value.emit()
lekvar.Reference.emit = Reference_emit

def Reference_emitValue(self):
    return self.value.emitValue()
lekvar.Reference.emitValue = Reference_emitValue

def Reference_emitType(self):
    return self.value.emitType()
lekvar.Reference.emitType = Reference_emitType

def Reference_emitAssignment(self):
    return self.value.emitAssignment()
lekvar.Reference.emitAssignment = Reference_emitAssignment

#
# class Attribute
#

def Attribute_emitValue(self):
    if self.value.static:
        return self.value.emitValue()

    self.value.bound_context.scope.emit()

    with State.selfScope(self.parent.emitAssignment()):
        return self.value.emitValue()
lekvar.Attribute.emitValue = Attribute_emitValue

def Attribute_emitType(self):
    return self.value.emitType()
lekvar.Attribute.emitType = Attribute_emitType

def Attribute_emitContext(self):
    return self.parent.emitAssignment()
lekvar.Attribute.emitContext = Attribute_emitContext

#
# class Literal
#

def Literal_emitValue(self):
    struct_type = self.type.emitType()

    if isinstance(self.data, str):
        data = State.builder.globalString(self.data, State.getTempName())
    elif isinstance(self.data, bool):
        data = llvm.Value.constInt(llvm.Int.new(1), self.data, False)
    elif isinstance(self.data, int):
        data = llvm.Value.constInt(llvm.Int.new(64), self.data, False)
    elif isinstance(self.data, float):
        data = llvm.Value.constFloat(llvm.Float.double(), self.data)
    else:
        raise InternalError("Not Implemented")

    return llvm.Value.constStruct(struct_type, [data])
lekvar.Literal.emitValue = Literal_emitValue

def Literal_emitAssignment(self):
    return State.pointer(self.emitValue())
lekvar.Literal.emitAssignment = Literal_emitAssignment

#
# class Variable
#

lekvar.Variable.llvm_context_index = -1

def Variable_emit(self):
    if self.llvm_value is not None or self.llvm_context_index >= 0: return

    if isinstance(self.bound_context.scope, lekvar.Class):
        self.bound_context.scope.emit()
    else:
        type = self.type.emitType()
        name = resolveName(self)
        if self.bound_context.scope.static:
            self.llvm_value = State.module.addVariable(type, name)
            self.llvm_value.initializer = llvm.Value.undef(type)
        else:
            self.llvm_value = State.builder.alloca(type, name)
lekvar.Variable.emit = Variable_emit

def Variable_emitValue(self, value=None):
    self.emit()

    return State.builder.load(self.emitAssignment(), State.getTempName())
lekvar.Variable.emitValue = Variable_emitValue

def Variable_emitAssignment(self):
    self.emit()

    if self.llvm_value is not None:
        return self.llvm_value

    return State.builder.structGEP(State.self, self.llvm_context_index, State.getTempName())
lekvar.Variable.emitAssignment = Variable_emitAssignment

#
# class Assignment
#

def Assignment_emitValue(self):
    value = self.value.emitValue()

    variable = self.variable.emitAssignment()
    State.builder.store(value, variable)
lekvar.Assignment.emitValue = Assignment_emitValue

#
# class Module
#

def Module_emit(self):
    if self.llvm_value is not None: return
    self.llvm_value = State.main

    State.addMainInstructions(self.main)

    for child in self.context:
        child.emit()
lekvar.Module.emit = Module_emit

def Module_emitValue(self):
    raise InternalError("Not Implemented") #TODO: Implement Method values
lekvar.Module.emitValue = Module_emitValue

#
# class Call
#

def Call_emitValue(self):
    called = self.function.emitValue()
    # Only use the function's context if it is static
    if self.called.resolveValue().static:
        context = self.function.emitContext()
    else:
        context = self.called.emitContext()

    if context is not None:
        context = self.function.emitContext(context)
        arguments = [context]
    else:
        arguments = []
    arguments += [val.emitValue() for val in self.values]

    # Get the llvm function type
    function_type = llvm.cast(llvm.cast(called.type, llvm.Pointer).element_type, llvm.Function)

    # Check the return type
    if function_type.return_type.kind == llvm.TypeKind.VoidTypeKind:
        name = ""
    else:
        name = State.getTempName()

    return State.builder.call(called, arguments, name)
lekvar.Call.emitValue = Call_emitValue

def Call_emitAssignment(self):
    return State.pointer(self.emitValue())
lekvar.Call.emitAssignment = Call_emitAssignment

#
# class Return
#

def Return_emitValue(self):
    exit = self.function.llvm_value.getLastBlock()

    if self.value is not None:
        value = self.value.emitValue()
        State.builder.store(value, self.function.llvm_return)

    return State.builder.br(exit)
lekvar.Return.emitValue = Return_emitValue

#
# class Context
#

lekvar.Context.llvm_type = None

def Context_emitType(self):
    if self.llvm_type is not None: return self.llvm_type

    types = []
    for index, child in self.children.items():
        child.llvm_context_index = index
        child_type = child.resolveType().emitType()
        types.append(llvm.Pointer.new(child_type, 0))

    if len(types) == 0:
        types = [llvm.Pointer.void_p()]

    self.llvm_type = llvm.Struct.newAnonym(types, False)

    return self.llvm_type
lekvar.Context.emitType = Context_emitType

#
# class DependentObject
#

lekvar.DependentObject.llvm_type = None

def DependentObject_emitType(self):
    if self.llvm_type is None:
        if self.target is None:
            raise InternalError("Invalid dependent type target")
        else:
            self.llvm_type = self.target.emitType()
    return self.llvm_type
lekvar.DependentObject.emitType = DependentObject_emitType

#
# class Function
#

lekvar.Function.llvm_closure_type = None
lekvar.Function.llvm_context = None

def Function_emit(self):
    if self.dependent: raise InternalError("Not Implemented")
    if self.llvm_value is not None: return

    self.llvm_closure_type = self.closed_context.emitType()

    name = resolveName(self)
    func_type = self.resolveType().emitType(self.llvm_closure_type)
    self.llvm_value = State.module.addFunction(name, func_type)

    entry = self.llvm_value.appendBlock("entry")
    exit = self.llvm_value.appendBlock("exit")

    with State.blockScope(entry):

        for child in self.local_context:
            child.emit()

        self.emitBody()
        State.builder.br(exit)

    with State.blockScope(exit):
        self.emitReturn()

lekvar.Function.emit = Function_emit

def Function_emitBody(self):
    self.emitEntry()

    self_value = State.builder.structGEP(self.llvm_context, 0, State.getTempName())
    self_value = State.builder.load(self_value, State.getTempName())
    with State.selfScope(self_value):

        # Allocate Arguments
        for index, arg in enumerate(self.arguments):
            val = self.llvm_value.getParam(index + 1)
            arg.llvm_value = State.builder.alloca(arg.type.emitType(), resolveName(arg))
            State.builder.store(val, arg.llvm_value)

        self.emitPostContext()

        # Emit instructions
        for instruction in self.instructions:
            instruction.emitValue()
lekvar.Function.emitBody = Function_emitBody

def Function_emitEntry(self):
    self.llvm_context = State.builder.alloca(self.llvm_closure_type, "context")
    State.builder.store(self.llvm_value.getParam(0), self.llvm_context)
lekvar.Function.emitEntry = Function_emitEntry

def Function_emitPostContext(self):
    # Allocate Return Variable
    if self.type.return_type is not None:
        self.llvm_return = State.builder.alloca(self.type.return_type.emitType(), "return")
lekvar.Function.emitPostContext = Function_emitPostContext

def Function_emitReturn(self):
    if self.llvm_return is not None:
        val = State.builder.load(self.llvm_return, State.getTempName())
        State.builder.ret(val)
    else:
        State.builder.retVoid()
lekvar.Function.emitReturn = Function_emitReturn

def Function_emitValue(self):
    self.emit()
    return self.llvm_value
lekvar.Function.emitValue = Function_emitValue

def Function_emitContext(self, self_value = None):
    if self_value is not None and len(self.closed_context) > 0:
        context = State.alloca(self.llvm_closure_type, State.getTempName())
        self_ptr = State.builder.structGEP(context, 0, State.getTempName())
        State.builder.store(self_value, self_ptr)
        return State.builder.load(context, State.getTempName())
    return llvm.Value.null(self.llvm_closure_type)
lekvar.Function.emitContext = Function_emitContext

#
# Contructor
#

def Constructor_emitEntry(self):
    lekvar.Function.emitEntry(self)

    self_var = State.builder.structGEP(self.llvm_context, 0, State.getTempName())

    self_val = State.builder.alloca(self.bound_context.scope.bound_context.scope.emitType(), "self")

    State.builder.store(self_val, self_var)
lekvar.Constructor.emitEntry = Constructor_emitEntry

def Constructor_emitPostContext(self):
    pass
lekvar.Constructor.emitPostContext = Constructor_emitPostContext

def Constructor_emitReturn(self):
    context = State.builder.structGEP(self.llvm_context, 0, State.getTempName())
    value = State.builder.load(context, State.getTempName())
    value = State.builder.load(value, State.getTempName())
    State.builder.ret(value)
lekvar.Constructor.emitReturn = Constructor_emitReturn

def Constructor_emitContext(self, self_value = None):
    return llvm.Value.null(self.llvm_closure_type)
lekvar.Constructor.emitContext = Constructor_emitContext

#
# class FunctionType
#

def FunctionType_emitType(self, context_type = None):
    if context_type is None:
        arguments = []
    else:
        arguments = [context_type]

    arguments += [type.emitType() for type in self.arguments]

    if self.return_type is not None:
        return_type = self.return_type.emitType()
    else:
        return_type = llvm.Type.void()
    return llvm.Function.new(return_type, arguments, False)
lekvar.FunctionType.emitType = FunctionType_emitType

#
# class ExternalFunction
#

def ExternalFunction_emit(self):
    if self.llvm_value is not None: return

    func_type = self.type.emitType()
    self.llvm_value = State.module.addFunction(self.external_name, func_type)
lekvar.ExternalFunction.emit = ExternalFunction_emit

def ExternalFunction_emitValue(self):
    self.emit()
    return self.llvm_value
lekvar.ExternalFunction.emitValue = ExternalFunction_emitValue

#
# class Method
#

def Method_emit(self):
    for overload in self.overload_context:
        overload.emit()
lekvar.Method.emit = Method_emit

#
# class Class
#

lekvar.Class.llvm_type = None

def Class_emit(self):
    if self.constructor is not None:
        self.constructor.emit()

    for child in self.instance_context:
        child.emit()

lekvar.Class.emit = Class_emit

def Class_emitType(self):
    if self.llvm_type is None:
        var_types = []

        for child in self.instance_context:
            if isinstance(child, lekvar.Variable):
                child.llvm_context_index = len(var_types)
                var_types.append(child.type.emitType())

        self.llvm_type = llvm.Struct.newAnonym(var_types, False)

    return self.llvm_type
lekvar.Class.emitType = Class_emitType

#
# class Loop
#

lekvar.Loop.after = None

def Loop_emitValue(self):
    # Grab the last block
    last_block = self.function.llvm_value.getLastBlock()
    # Create blocks
    loop_block = last_block.insertBlock("loop")
    self.after = last_block.insertBlock("after")

    # Reposition builder
    State.builder.br(loop_block)
    State.builder.positionAtEnd(loop_block)

    for instruction in self.instructions:
        instruction.emitValue()
    # Loop
    # Rely on break to end the loop
    State.builder.br(loop_block)

    # Move the after block before the last block
    self.after.moveBefore(last_block)
    State.builder.positionAtEnd(self.after)
lekvar.Loop.emitValue = Loop_emitValue

#
# class Break
#

def Break_emitValue(self):
    # Branch to the after block of the loop
    State.builder.br(self.loop.after)
lekvar.Break.emitValue = Break_emitValue

#
# class Branch
#

def Branch_emitValue(self):
    # Grab the last block
    last_block = self.function.llvm_value.getLastBlock()
    # Create blocks
    if_block = last_block.insertBlock("if")
    else_block = last_block.insertBlock("else")
    after = last_block.insertBlock("after")

    # Emit condition
    condition = State.builder.extractValue(self.condition.emitValue(), 0, State.getTempName())
    State.builder.condBr(condition, if_block, else_block)

    for block, instructions in [(if_block, self.true_instructions), (else_block, self.false_instructions)]:
        State.builder.positionAtEnd(block)
        for instruction in instructions:
            instruction.emitValue()
        State.builder.br(after)

    after.moveBefore(last_block)
    State.builder.positionAtEnd(after)
lekvar.Branch.emitValue = Branch_emitValue

#
# BUILTINS
#

from . import builtins

#
# class LLVMType
#

LLVM_MAP = None

def LLVMType_emit(self):
    pass
builtins.LLVMType.emit = LLVMType_emit

def LLVMType_emitType(self):
    global LLVM_MAP
    if LLVM_MAP is None:
        LLVM_MAP = {
            "String": llvm.Pointer.new(llvm.Int.new(8), 0),
            "Bool": llvm.Int.new(1),
            "Int8": llvm.Int.new(8),
            "Int16": llvm.Int.new(16),
            "Int32": llvm.Int.new(32),
            "Int64": llvm.Int.new(64),
            "Int128": llvm.Int.new(128),
            "Float16": llvm.Float.half(),
            "Float32": llvm.Float.float(),
            "Float64": llvm.Float.double(),
        }
    return LLVM_MAP[self.name]
builtins.LLVMType.emitType = LLVMType_emitType

#
# class LLVMFunction
#

builtins.LLVMFunction.llvm_value = None

def LLVMFunction_emit(self):
    if self.llvm_value is None:
        self.generator(self)
builtins.LLVMFunction.emit = LLVMFunction_emit

def LLVMFunction_emitValue(self):
    self.emit()
    return self.llvm_value
builtins.LLVMFunction.emitValue = LLVMFunction_emitValue
