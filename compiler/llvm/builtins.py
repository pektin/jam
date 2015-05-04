from functools import partial

from .emitter import *
from ..lekvar import lekvar
from . import bindings as llvm

def builtins():
    string = LLVMType("String")
    ints = [
        LLVMType("Int8"),
        LLVMType("Int16"),
        LLVMType("Int32"),
        LLVMType("Int64"),
        LLVMType("Int128"),
    ]
    floats = [
        LLVMType("Float16"),
        LLVMType("Float32"),
        LLVMType("Float64"),
    ]
    return lekvar.Module("_builtins",
        ints + floats + [
        lekvar.ExternalFunction("print", "puts", [string], ints[2]),
        string,
        lekvar.Method("intAdd",
            [LLVMFunction("", [type, type], type, partial(llvmInstructionWrapper, llvm.Builder.iAdd))
            for type in ints],
        ),
        lekvar.Method("intSub",
            [LLVMFunction("", [type, type], type, partial(llvmInstructionWrapper, llvm.Builder.iAdd))
            for type in ints],
        ),
    ], lekvar.Function("main", [], [], None))

def llvmInstructionWrapper(instruction, self):
    name = resolveName(self)
    func_type = self.type.emitType()
    self.llvm_value = State.module.addFunction(name, func_type)
    entry = self.llvm_value.appendBlock("")

    with State.blockScope(entry):
        lhs = self.llvm_value.getParam(0)
        rhs = self.llvm_value.getParam(1)
        return_value = instruction(State.builder, lhs, rhs, "")
        State.builder.ret(return_value)

#
# Temporary
#

class LLVMType(lekvar.Type):
    def __init__(self, name:str):
        super().__init__(name)

    def copy(self):
        raise InternalError("Cannot copy LLVMType")

    def verify(self):
        pass

    def resolveType(self):
        raise InternalError("Not Implemented")

    @property
    def children(self):
        raise InternalError("Not Implemented")

    def addChild(self, child):
        raise InternalError("Not Implemented")

    def checkCompatibility(self, other:lekvar.Type):
        if isinstance(other, lekvar.Reference):
            other = other.value

        if isinstance(other, LLVMType):
            if self.name == other.name:
                return True
        return False

    def __repr__(self):
        return "{}<{}>".format(self.__class__.__name__, self.name)

class LLVMFunction(lekvar.ExternalFunction):
    generator = None

    def __init__(self, name:str, arguments:[lekvar.Type], return_type:lekvar.Type, generator):
        super().__init__(name, name, arguments, return_type)
        self.generator = generator
