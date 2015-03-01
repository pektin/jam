from contextlib import contextmanager
from functools import partial
from abc import abstractmethod as abstract

from ..lekvar import lekvar
from ..errors import *

from . import bindings as llvm

# Temporary until LLVMType is replaced
LLVMMAP = {
    "String": llvm.Pointer.new(llvm.Int.new(8), 0),
    "Int": llvm.Int.new(32),
}

def emit(module:lekvar.Module):
    state = State(b"main")
    module.emit(state)
    state.finalize()
    return state.module.toString()

class State:
    def __init__(self, name:str):
        self.builder = llvm.Builder.new()
        self.module = llvm.Module.fromName(name)
        self.main = []

    def finalize(self):
        main_type = lekvar.FunctionType([], lekvar.LLVMType("Int")).emitType(self)
        main = self.module.addFunction("main", main_type)

        entry = main.appendBlock("entry")
        with self.blockScope(entry):
            for func in self.main:
                call = lekvar.Call("", [])
                call.called = func
                call.emitValue(self)

            return_value = llvm.Value.constInt(lekvar.LLVMType("Int").emitType(self), 0, False)
            self.builder.ret(return_value)

    @contextmanager
    def blockScope(self, block:llvm.Block):
        previous_block = self.builder.position
        self.builder.positionAtEnd(block)
        yield
        self.builder.positionAtEnd(previous_block)

    def getTempName(self):
        return "temp"


def main_call(func:lekvar.Function):
    call = lekvar.Call("", [])
    call.called = func
    return call

# Abstract extensions

lekvar.ScopeObject.llvm_value = None
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

def resolveName(scope:lekvar.ScopeObject):
    # Resolves the name of a scope, starting with a extraneous .
    name = "lekvar"
    while scope.parent is not None:
        name += "." + scope.name
        scope = scope.parent
    return name

# Implements

# For this that don't emit anything
def blank_emitValue(self, state:State):
    return None
lekvar.Comment.emitValue = blank_emitValue

#
# class Reference
#

def Reference_emitValue(self, state:State):
    return self.value.emitValue(state)
lekvar.Reference.emitValue = Reference_emitValue

#
# class Literal
#

def Literal_emitValue(self, state:State):
    type = self.type.llvm_type

    if type == "String":
        return state.builder.globalString(self.data, state.getTempName())
    else:
        raise NotImplemented()
lekvar.Literal.emitValue = Literal_emitValue

#
# class Variable
#

def Variable_emit(self, state:State):
    if self.llvm_value is not None: return

    type = self.type.emitType(state)
    name = resolveName(self)
    self.llvm_value = state.builder.alloca(type, name)
lekvar.Variable.emit = Variable_emit

def Variable_emitValue(self, state:State):
    self.emit(state)
    return state.builder.load(self.llvm_value, state.getTempName())
lekvar.Variable.emitValue = Variable_emitValue

#
# class Assignment
#

def Assignment_emitValue(self, state:State):
    value = self.value.emitValue(state)
    self.variable.emit(state)
    state.builder.store(value, self.variable.llvm_value)
lekvar.Assignment.emitValue = Assignment_emitValue

#
# class Module
#

def Module_emit(self, state:State):
    if self.llvm_value is not None: return

    self.llvm_value = self.main.emitValue(state)
    state.main.append(self.main)

    for child in self.children.values():
        child.emit(state)
lekvar.Module.emit = Module_emit

#
# class Call
#

def Call_emitValue(self, state:State):
    arguments = [val.emitValue(state) for val in self.values]
    if self.called.return_type is None:
        name = ""
    else:
        name = state.getTempName()
    return state.builder.call(self.called.emitValue(state), arguments, name)
lekvar.Call.emitValue = Call_emitValue

#
# class Return
#

def Return_emitValue(self, state:State):
    exit = self.parent.llvm_value.getLastBlock()
    if self.value is None:
        state.builder.br(return_)
    else:
        value = self.value.emitValue(state)
        state.builder.store(value, self.parent.llvm_return)
        state.builder.br(exit)
lekvar.Return.emitValue = Return_emitValue

#
# class Function
#

def Function_emit(self, state:State):
    if self.llvm_value is not None: return

    name = resolveName(self)
    func_type = self.resolveType().emitType(state)
    self.llvm_value = state.module.addFunction(name, func_type)

    entry = self.llvm_value.appendBlock("entry")
    exit = self.llvm_value.appendBlock("exit")
    with state.blockScope(entry):
        # Allocate Arguments
        for index, arg in enumerate(self.arguments):
            val = self.llvm_value.getParam(index)
            arg.llvm_value = state.builder.alloca(arg.type.emitType(state), resolveName(arg))
            state.builder.store(val, arg.llvm_value)

        # Allocate Return Variable
        if self.return_type is not None:
            self.llvm_return = state.builder.alloca(self.return_type.emitType(state), "return")

        for instruction in self.instructions:
            instruction.emitValue(state)

        state.builder.br(exit)

    with state.blockScope(exit):
        if self.llvm_return is not None:
            val = state.builder.load(self.llvm_return, state.getTempName())
            state.builder.ret(val)
        else:
            state.builder.retVoid()
lekvar.Function.emit = Function_emit

def Function_emitValue(self, state:State):
    self.emit(state)
    return self.llvm_value
lekvar.Function.emitValue = Function_emitValue

#
# class FunctionType
#

def FunctionType_emitType(self, state:State):
    arguments = [type.emitType(state) for type in self.signature]
    if self.return_type is not None:
        return_type = self.return_type.emitType(state)
    else:
        return_type = llvm.Type.void()
    return llvm.Function.new(return_type, arguments, False)
lekvar.FunctionType.emitType = FunctionType_emitType

#
# class ExternalFunction
#

def ExternalFunction_emit(self, state:State):
    if self.llvm_value is not None: return

    func_type = self.resolveType().emitType(state)
    self.llvm_value = state.module.addFunction(self.external_name, func_type)
lekvar.ExternalFunction.emit = ExternalFunction_emit

def ExternalFunction_emitValue(self, state:State):
    self.emit(state)
    return self.llvm_value
lekvar.ExternalFunction.emitValue = ExternalFunction_emitValue

#
# class Method
#

def Method_emit(self, state:State):
    if self.llvm_value is not None: return

    for overload in self.overloads:
        overload.emit(state)
lekvar.Method.emit = Method_emit

#
# class LLVMType
#

def LLVMType_emitType(self, state:State):
    return LLVMMAP[self.llvm_type]
lekvar.LLVMType.emitType = LLVMType_emitType
