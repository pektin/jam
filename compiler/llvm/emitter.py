import logging
from contextlib import contextmanager
from functools import partial
from abc import abstractmethod as abstract

from ..lekvar import lekvar
from ..errors import *

from . import bindings as llvm
from .builtins import LLVMType

def emit(module:lekvar.Module, logger = logging.getLogger()):
    State.logger = logger.getChild("llvm")
    llvm.State.logger = State.logger.getChild("bindings")

    with State.begin("main", logger):
        module.emit()

    State.logger.info("LLVM output: {}".format(State.module.verify(llvm.FailureAction.PrintMessageAction, None)))
    return State.module.toString()

class State:
    @classmethod
    @contextmanager
    def begin(cls, name:str, logger:logging.Logger):
        cls.logger = logger

        cls.self = None
        cls.builder = llvm.Builder.new()
        cls.module = llvm.Module.fromName(name)
        cls.main = []
        yield
        main_type = llvm.Function.new(llvm.Int.new(32), [], False)
        main = cls.module.addFunction("main", main_type)

        entry = main.appendBlock("entry")
        with cls.blockScope(entry):
            for func in cls.main:
                call = lekvar.Call("", [])
                call.function = func
                call.emitValue()

            return_value = llvm.Value.constInt(llvm.Int.new(32), 0, False)
            cls.builder.ret(return_value)

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


def main_call(func:lekvar.Function):
    call = lekvar.Call("", [])
    call.function = func
    return call

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

#
# class Attribute
#

def Attribute_emitValue(self):
    self.attribute.bound_context.scope.emit()
    return self.attribute.emitValue(self.value.emit())
lekvar.Attribute.emitValue = Attribute_emitValue

#
# class Literal
#

def Literal_emitValue(self):
    type = self.type.emitType()

    if type == LLVM_MAP["String"]:
        return State.builder.globalString(self.data, State.getTempName())
    else:
        raise InternalError("Not Implemented")
lekvar.Literal.emitValue = Literal_emitValue

#
# class Variable
#

def Variable_emit(self):
    if self.llvm_value is not None: return self.llvm_value

    type = self.type.emitType()
    name = resolveName(self)
    self.llvm_value = State.builder.alloca(type, name)
    return self.llvm_value
lekvar.Variable.emit = Variable_emit

def Variable_emitValue(self, value:llvm.Value = None):
    self.emit()

    if value:
        return State.builder.load(State.builder.structGEP(value, self.llvm_value, State.getTempName()), State.getTempName())
    return State.builder.load(self.llvm_value, State.getTempName())
lekvar.Variable.emitValue = Variable_emitValue

#
# class Assignment
#

def Assignment_emitValue(self):
    value = self.value.emitValue()

    if isinstance(self.variable.bound_context.scope, lekvar.Class):
        variable = State.builder.structGEP(self.scope.llvm_return, self.variable.llvm_value, State.getTempName())
    else:
        variable = self.variable.emit()
    State.builder.store(value, variable)
lekvar.Assignment.emitValue = Assignment_emitValue

#
# class Module
#

def Module_emit(self):
    if self.llvm_value is not None: return

    self.llvm_value = self.main.emitValue()
    State.main.append(self.main)

    for child in self.context.children.values():
        child.emit()
lekvar.Module.emit = Module_emit

#
# class Call
#

def Call_emitValue(self):
    arguments = [val.emitValue() for val in self.values]
    called = self.function.emitValue()
    if called is None: raise InternalError("Fuck")
    # Get the llvm function type
    function_type = llvm.cast(llvm.cast(called.type, llvm.Pointer).element_type, llvm.Function)

    # Check the return type
    if function_type.return_type.kind == llvm.TypeKind.VoidTypeKind:
        name = ""
    else:
        name = State.getTempName()
    return State.builder.call(called, arguments, name)
lekvar.Call.emitValue = Call_emitValue

#
# class Return
#

def Return_emitValue(self):
    exit = self.function.llvm_value.getLastBlock()
    if self.value is None:
        State.builder.br(exit)
    else:
        value = self.value.emitValue()
        State.builder.store(value, self.function.llvm_return)
        State.builder.br(exit)
lekvar.Return.emitValue = Return_emitValue

#
# class DependentType
#

lekvar.DependentType.llvm_type = None

def DependentType_emitType(self):
    if self.llvm_type is None:
        if self.target is None:
            raise InternalError("Invalid dependent type target")
        else:
            self.llvm_type = self.target.emitType()
    return self.llvm_type
lekvar.DependentType.emitType = DependentType_emitType

#
# class Function
#

def Function_emit(self):
    if self.dependent: return
    if self.llvm_value is not None: return

    name = resolveName(self)
    func_type = self.resolveType().emitType()
    self.llvm_value = State.module.addFunction(name, func_type)

    entry = self.llvm_value.appendBlock("entry")
    exit = self.llvm_value.appendBlock("exit")

    with State.blockScope(entry):
        self.emitBody()
        State.builder.br(exit)

    with State.blockScope(exit):
        if self.llvm_return is not None:
            val = State.builder.load(self.llvm_return, State.getTempName())
            State.builder.ret(val)
        else:
            State.builder.retVoid()
lekvar.Function.emit = Function_emit

def Function_emitBody(self):
    # Allocate Arguments
    for index, arg in enumerate(self.arguments):
        val = self.llvm_value.getParam(index)
        arg.llvm_value = State.builder.alloca(arg.type.emitType(), resolveName(arg))
        State.builder.store(val, arg.llvm_value)

    # Allocate Return Variable
    if self.type.return_type is not None:
        self.llvm_return = State.builder.alloca(self.type.return_type.emitType(), "return")

    for instruction in self.instructions:
        instruction.emitValue()
lekvar.Function.emitBody = Function_emitBody

def Function_emitValue(self):
    self.emit()
    return self.llvm_value
lekvar.Function.emitValue = Function_emitValue

#
# class FunctionType
#

def FunctionType_emitType(self):
    arguments = [type.emitType() for type in self.arguments]
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
    if self.llvm_value is not None: return

    for overload in self.overload_context.children.values():
        overload.emit()
lekvar.Method.emit = Method_emit

#
# class Class
#

lekvar.Class.llvm_type = None

def Class_emit(self):
    if self.llvm_type is not None: return

    var_types = []
    for child in self.instance_context.children.values():
        if isinstance(child, lekvar.Variable):
            child.llvm_value = len(var_types)
            var_types.append(child.type.emitType())

    self.llvm_type = llvm.Struct.new(var_types, False)
lekvar.Class.emit = Class_emit

def Class_emitType(self):
    self.emit()
    return self.llvm_type
lekvar.Class.emitType = Class_emitType

#
# class LLVMType
#

LLVM_MAP = None

def LLVMType_emitType(self):
    global LLVM_MAP
    if LLVM_MAP is None:
        LLVM_MAP = {
            "String": llvm.Pointer.new(llvm.Int.new(8), 0),
            "Int8": llvm.Int.new(8),
            "Int16": llvm.Int.new(16),
            "Int32": llvm.Int.new(32),
            "Int64": llvm.Int.new(64),
            "Float16": llvm.Float.half(),
            "Float32": llvm.Float.float(),
            "Float64": llvm.Float.double(),
        }
    return LLVM_MAP[self.name]
LLVMType.emitType = LLVMType_emitType
