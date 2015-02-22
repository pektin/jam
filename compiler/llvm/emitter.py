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


def main_call(func:lekvar.Function):
    call = lekvar.Call("", [])
    call.called = func
    return call

# Abstract extensions

lekvar.Scope.llvm_value = None

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

def Module_emit(self, state:State):
    self.main.emit(state)
    state.main.append(self.main)

    for child in self.children.values():
        child.emit(state)
lekvar.Module.emit = Module_emit

def Call_emitValue(self, state:State):
    arguments = [val.emitValue(state) for val in self.values]
    return state.builder.call(self.called.emitValue(state), arguments, "")
lekvar.Call.emitValue = Call_emitValue

def Function_emit(self, state:State):
    func_type = self.resolveType().emitType(state)

    name = resolveName(self)
    self.llvm_value = state.module.addFunction(name, func_type)

    entry = self.llvm_value.appendBlock("entry")
    return_ = self.llvm_value.appendBlock("return")
    with state.blockScope(entry):
        for instruction in self.instructions:
            instruction.emitValue(state)
        state.builder.br(return_)

    with state.blockScope(return_):
        state.builder.retVoid() #TODO: Returns
lekvar.Function.emit = Function_emit

def Function_emitValue(self, state:State):
    if self.llvm_value is None:
        self.emit(state)
    return self.llvm_value
lekvar.Function.emitValue = Function_emitValue

def FunctionType_emitType(self, state:State):
    arguments = [type.emitType(state) for type in self.signature]
    if self.return_type is not None:
        return_type = self.return_type.emitType(state)
    else:
        return_type = llvm.Type.void()
    return llvm.Function.new(return_type, arguments, False)
lekvar.FunctionType.emitType = FunctionType_emitType

def ExternalFunction_emit(self, state:State):
    func_type = self.resolveType().emitType(state)
    self.llvm_value = state.module.addFunction(self.external_name, func_type)
lekvar.ExternalFunction.emit = ExternalFunction_emit

def ExternalFunction_emitValue(self, state:State):
    if self.llvm_value is None:
        self.emit(state)
    return self.llvm_value
lekvar.ExternalFunction.emitValue = ExternalFunction_emitValue

def Literal_emitValue(self, state:State):
    type = self.type.llvm_type

    if type == "String":
        return state.builder.globalString(self.data, "")
    else:
        raise NotImplemented()
lekvar.Literal.emitValue = Literal_emitValue

def LLVMType_emitType(self, state:State):
    return LLVMMAP[self.llvm_type]
lekvar.LLVMType.emitType = LLVMType_emitType
