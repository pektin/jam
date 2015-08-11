from abc import abstractmethod as abstract

from .. import lekvar
from ..errors import *

from .state import State
from .util import *
from . import bindings as llvm

# Abstract extensions

lekvar.BoundObject.llvm_value = None
lekvar.Function.llvm_return = None

# Extension abstract methods apparently don't work
#@patch
#@abstract
#def Object_emitValue(self, state:State) -> llvm.Value:
#    pass

#@patch
#@abstract
#def Type_emitType(self, state:State) -> llvm.Type:
#    pass

lekvar.Object.emitContext = blankEmit
lekvar.Comment.emitValue = blankEmit

#
# class Reference
#

@patch
def Reference_emit(self):
    return self.value.emit()

@patch
def Reference_emitValue(self):
    return self.value.emitValue()

@patch
def Reference_emitType(self):
    return self.value.emitType()

@patch
def Reference_emitAssignment(self):
    return self.value.emitAssignment()

#
# class Attribute
#

@patch
def Attribute_emitValue(self):
    self.value.bound_context.scope.emit()

    with State.selfScope(self.parent.emitAssignment()):
        return self.value.emitValue()

@patch
def Attribute_emitType(self):
    return self.value.emitType()

@patch
def Attribute_emitContext(self):
    return self.parent.emitAssignment()

#
# class Literal
#

@patch
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

@patch
def Literal_emitAssignment(self):
    return State.pointer(self.emitValue())

#
# class Variable
#

lekvar.Variable.llvm_context_index = -1

@patch
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

@patch
def Variable_emitValue(self, value=None):
    self.emit()

    return State.builder.load(self.emitAssignment(), State.getTempName())

@patch
def Variable_emitAssignment(self):
    self.emit()

    if self.llvm_value is not None:
        return self.llvm_value

    return State.builder.structGEP(State.self, self.llvm_context_index, State.getTempName())

#
# class Assignment
#

@patch
def Assignment_emitValue(self):
    value = self.value.emitValue()

    variable = self.variable.emitAssignment()
    State.builder.store(value, variable)

#
# class Module
#

@patch
def Module_emit(self):
    if self.llvm_value is not None: return
    self.llvm_value = State.main

    State.addMainInstructions(self.main)

    for child in self.context:
        child.emit()

@patch
def Module_emitValue(self):
    raise InternalError("Not Implemented") #TODO: Implement Method values

#
# class Call
#

@patch
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

@patch
def Call_emitAssignment(self):
    return State.pointer(self.emitValue())

#
# class Return
#

@patch
def Return_emitValue(self):
    exit = self.function.llvm_value.getLastBlock()

    if self.value is not None:
        value = self.value.emitValue()
        State.builder.store(value, self.function.llvm_return)

    return State.builder.br(exit)

#
# class Context
#

lekvar.Context.llvm_type = None

@patch
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

#
# class DependentObject
#

lekvar.DependentObject.llvm_type = None

@patch
def DependentObject_emitType(self):
    if self.llvm_type is None:
        if self.target is None:
            raise InternalError("Invalid dependent type target")
        else:
            self.llvm_type = self.target.emitType()
    return self.llvm_type

#
# class Function
#

lekvar.Function.llvm_closure_type = None
lekvar.Function.llvm_context = None

@patch
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

        # Only emit br if it hasn't already
        if not self.emitBody():
            State.builder.br(exit)

    with State.blockScope(exit):
        self.emitReturn()

@patch
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

        return State.emitInstructions(self.instructions)

@patch
def Function_emitEntry(self):
    self.llvm_context = State.builder.alloca(self.llvm_closure_type, "context")
    State.builder.store(self.llvm_value.getParam(0), self.llvm_context)

@patch
def Function_emitPostContext(self):
    # Allocate Return Variable
    if self.type.return_type is not None:
        self.llvm_return = State.builder.alloca(self.type.return_type.emitType(), "return")

@patch
def Function_emitReturn(self):
    if self.llvm_return is not None:
        val = State.builder.load(self.llvm_return, State.getTempName())
        State.builder.ret(val)
    else:
        State.builder.retVoid()

@patch
def Function_emitValue(self):
    self.emit()
    return self.llvm_value

@patch
def Function_emitContext(self, self_value = None):
    if self_value is not None and len(self.closed_context) > 0:
        context = State.alloca(self.llvm_closure_type, State.getTempName())
        self_ptr = State.builder.structGEP(context, 0, State.getTempName())
        State.builder.store(self_value, self_ptr)
        return State.builder.load(context, State.getTempName())
    return llvm.Value.null(self.llvm_closure_type)

#
# Contructor
#

@patch
def Constructor_emitEntry(self):
    lekvar.Function.emitEntry(self)

    self_var = State.builder.structGEP(self.llvm_context, 0, State.getTempName())

    self_val = State.builder.alloca(self.bound_context.scope.bound_context.scope.emitType(), "self")

    State.builder.store(self_val, self_var)

@patch
def Constructor_emitPostContext(self):
    pass

@patch
def Constructor_emitReturn(self):
    context = State.builder.structGEP(self.llvm_context, 0, State.getTempName())
    value = State.builder.load(context, State.getTempName())
    value = State.builder.load(value, State.getTempName())
    State.builder.ret(value)

@patch
def Constructor_emitContext(self, self_value = None):
    return llvm.Value.null(self.llvm_closure_type)

#
# class FunctionType
#

@patch
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

#
# class ExternalFunction
#

@patch
def ExternalFunction_emit(self):
    if self.llvm_value is not None: return

    func_type = self.type.emitType()
    self.llvm_value = State.module.addFunction(self.external_name, func_type)

@patch
def ExternalFunction_emitValue(self):
    self.emit()
    return self.llvm_value

#
# class Method
#

@patch
def Method_emit(self):
    for overload in self.overload_context:
        overload.emit()

#
# class Class
#

lekvar.Class.llvm_type = None

@patch
def Class_emit(self):
    if self.constructor is not None:
        self.constructor.emit()

    for child in self.instance_context:
        child.emit()

@patch
def Class_emitType(self):
    if self.llvm_type is None:
        var_types = []

        for child in self.instance_context:
            if isinstance(child, lekvar.Variable):
                child.llvm_context_index = len(var_types)
                var_types.append(child.type.emitType())

        self.llvm_type = llvm.Struct.newAnonym(var_types, False)

    return self.llvm_type

#
# class Loop
#

lekvar.Loop.after = None

@patch
def Loop_emitValue(self):
    # Grab the last block
    last_block = self.function.llvm_value.getLastBlock()
    # Create blocks
    loop_block = last_block.insertBlock("loop")
    self.after = last_block.insertBlock("after")

    # Reposition builder
    State.builder.br(loop_block)
    State.builder.positionAtEnd(loop_block)

    # Only loop if we don't return
    if not State.emitInstructions(self.instructions):
        # Loop
        # Rely on break to end the loop
        State.builder.br(loop_block)

    # Move the after block before the last block
    self.after.moveBefore(last_block)
    State.builder.positionAtEnd(self.after)

#
# class Break
#

@patch
def Break_emitValue(self):
    return State.builder.br(self.loop.after)

#
# class Branch
#

@patch
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

        if not State.emitInstructions(instructions):
            # Only br to after if we don't return
            State.builder.br(after)

    after.moveBefore(last_block)
    State.builder.positionAtEnd(after)
