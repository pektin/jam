import logging
from contextlib import contextmanager
from functools import partial
from abc import abstractmethod as abstract

from ..lekvar import lekvar
from ..errors import *

from . import bindings as llvm
from .builtins import LLVMType

def emit(module:lekvar.Module, logger:logging.Logger = None):
    if logger is None: logger = logging.getLogger()

    with State.begin(b"main", logger):
        module.emit()

    return State.module.toString()

class State:
    @classmethod
    @contextmanager
    def begin(cls, name:str, logger:logging.Logger):
        cls.logger = logger

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
                call.called = func
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
    def getTempName(self):
        return "temp"


def main_call(func:lekvar.Function):
    call = lekvar.Call("", [])
    call.called = func
    return call

# Abstract extensions

lekvar.Scope.llvm_value = None
lekvar.Function.llvm_return = None

# Extension abstract methods apparently don't work
"""@abstract
def Object_emitValue(self, state:State) -> llvm.Value:
    pass
lekvar.Object.emitValue = Object_emitValue

@abstract
def Scope_emit(self, state:State) -> None:
    pass
lekvar.Scope.emit = Scope_emit

@abstract
def Type_emitType(self, state:State) -> llvm.Type:
    pass
lekvar.Type.emitType = Type_emitType
lekvar.Type.llvm_type = None"""

#
# Tools
#

def resolveName(scope:lekvar.Scope):
    # Resolves the name of a scope, starting with a extraneous .
    name = ""
    while scope.parent is not None:
        name = "." + scope.name + name
        scope = scope.parent
    return "lekvar" + name

# Implements

# For this that don't emit anything
def blank_emitValue(self):
    return None
lekvar.Comment.emitValue = blank_emitValue

#
# class Reference
#

def Reference_emitValue(self):
    return self.value.emitValue()
lekvar.Reference.emitValue = Reference_emitValue

def Reference_emitType(self):
    if self.value is None: print("Missing:", self)
    return self.value.emitType()
lekvar.Reference.emitType = Reference_emitType

#
# class Literal
#

def Literal_emitValue(self):
    type = self.type.emitType()

    if type == LLVM_MAP["String"]:
        return State.builder.globalString(self.data, State.getTempName())
    else:
        raise NotImplemented()
lekvar.Literal.emitValue = Literal_emitValue

#
# class Variable
#

def Variable_emit(self):
    if self.llvm_value is not None: return

    type = self.type.emitType()
    name = resolveName(self)
    self.llvm_value = State.builder.alloca(type, name)
#lekvar.Variable.emit = Variable_emit

def Variable_emitValue(self):
    self.emit()
    return State.builder.load(self.llvm_value, State.getTempName())
#lekvar.Variable.emitValue = Variable_emitValue

#
# class Assignment
#

def Assignment_emitValue(self):
    value = self.value.emitValue()
    self.variable.emit()
    State.builder.store(value, self.variable.llvm_value)
#lekvar.Assignment.emitValue = Assignment_emitValue

#
# class Module
#

def Module_emit(self):
    if self.llvm_value is not None: return

    self.llvm_value = self.main.emitValue()
    State.main.append(self.main)

    for child in self.children.values():
        child.emit()
lekvar.Module.emit = Module_emit

#
# class Call
#

def Call_emitValue(self):
    arguments = [val.emitValue() for val in self.values]
    if self.called.type.return_type is None:
        name = ""
    else:
        name = State.getTempName()
    return State.builder.call(self.called.emitValue(), arguments, name)
lekvar.Call.emitValue = Call_emitValue

#
# class Return
#

def Return_emitValue(self):
    exit = self.parent.llvm_value.getLastBlock()
    if self.value is None:
        State.builder.br(return_)
    else:
        value = self.value.emitValue()
        State.builder.store(value, self.parent.llvm_return)
        State.builder.br(exit)
#lekvar.Return.emitValue = Return_emitValue

#
# class Function
#

def Function_emit(self):
    if self.llvm_value is not None: return

    name = resolveName(self)
    func_type = self.resolveType(self).emitType()
    self.llvm_value = State.module.addFunction(name, func_type)

    entry = self.llvm_value.appendBlock("entry")
    exit = self.llvm_value.appendBlock("exit")
    with State.blockScope(entry):
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

        State.builder.br(exit)

    with State.blockScope(exit):
        if self.llvm_return is not None:
            val = State.builder.load(self.llvm_return, State.getTempName())
            State.builder.ret(val)
        else:
            State.builder.retVoid()
lekvar.Function.emit = Function_emit

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

    for overload in self.overloads:
        overload.emit()
lekvar.Method.emit = Method_emit

#
# class LLVMType
#

LLVM_MAP = None

def LLVMType_emitType(self):
    global LLVM_MAP
    if LLVM_MAP is None:
        LLVM_MAP = {
            "String": llvm.Pointer.new(llvm.Int.new(8), 0),
            "Int32": llvm.Int.new(32),
            "Int8": llvm.Int.new(8),
        }
    return LLVM_MAP[self.name]
LLVMType.emitType = LLVMType_emitType
