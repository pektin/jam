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
        string,
        lekvar.Method("intAdd",
            [LLVMFunction("", [type, type], type, partial(llvmInstructionWrapper, llvm.Builder.iAdd))
            for type in ints],
        ),
        lekvar.Method("intSub",
            [LLVMFunction("", [type, type], type, partial(llvmInstructionWrapper, llvm.Builder.iSub))
            for type in ints],
        ),
        lekvar.Method("intMul",
            [LLVMFunction("", [type, type], type, partial(llvmInstructionWrapper, llvm.Builder.iMul))
            for type in ints],
        ),
        lekvar.Method("intDiv",
            [LLVMFunction("", [type, type], type, partial(llvmInstructionWrapper, llvm.Builder.siDiv))
            for type in ints],
        ),
        lekvar.Method("floatAdd",
            [LLVMFunction("", [type, type], type, partial(llvmInstructionWrapper, llvm.Builder.fAdd))
            for type in floats],
        ),
        lekvar.Method("floatSub",
            [LLVMFunction("", [type, type], type, partial(llvmInstructionWrapper, llvm.Builder.fSub))
            for type in floats],
        ),
        lekvar.Method("floatMul",
            [LLVMFunction("", [type, type], type, partial(llvmInstructionWrapper, llvm.Builder.fMul))
            for type in floats],
        ),
        lekvar.Method("floatDiv",
            [LLVMFunction("", [type, type], type, partial(llvmInstructionWrapper, llvm.Builder.fDiv))
            for type in floats],
        ),
        lekvar.Method("puts",
            [LLVMFunction("", [type], None, partial(llvmPrintfWrapper, type))
            for type in (ints + floats + [string])],
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

PRINTF_MAP = {
    "String": "s",

    "Int8": "hhd",
    "Int16": "hd",
    "Int32": "d",
    "Int64": "ld",
    "Int128": "lld",

    "Float16": "hf",
    "Float32": "f",
    "Float64": "lf",
}

def llvmPrintfWrapper(type, self):
    func_type = llvm.Function.new(llvm.Type.void(), [LLVMType("String").emitType()], True)
    printf = State.module.addFunction("printf", func_type)

    name = resolveName(self)
    func_type = self.type.emitType()
    self.llvm_value = State.module.addFunction(name, func_type)
    entry = self.llvm_value.appendBlock("")

    with State.blockScope(entry):
        fmt_str_data = "%{}\n".format(PRINTF_MAP[type.name])
        fmt_string = State.builder.globalString(fmt_str_data, State.getTempName())

        value = self.llvm_value.getParam(0)
        State.builder.call(printf, [fmt_string, value], "")
        State.builder.retVoid()

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
        other = other.resolveValue()

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
