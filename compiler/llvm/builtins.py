from functools import partial

from .emitter import *
from .. import lekvar
from . import bindings as llvm

printf = None

def builtins():
    global printf
    printf = None

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
    bool = LLVMType("Bool")

    builtin_objects = [string, bool] + ints + floats

    # (the types the method applies to, the name, the instruction, additional arguments)
    methods = [
        (ints, "intAdd", llvm.Builder.iAdd, []),
        (ints, "intSub", llvm.Builder.iSub, []),
        (ints, "intMul", llvm.Builder.iMul, []),
        (ints, "intDiv", llvm.Builder.siDiv, []),
        (ints, "intEqual", llvm.Builder.iCmp, [llvm.IntPredicate.equal]),
        (ints, "intUnequal", llvm.Builder.iCmp, [llvm.IntPredicate.unequal]),
        (ints, "intGreaterThan", llvm.Builder.iCmp, [llvm.IntPredicate.signed_greater_than]),
        (ints, "intGreaterOrEqualTo", llvm.Builder.iCmp, [llvm.IntPredicate.signed_greater_or_equal_to]),
        (ints, "intSmallerThan", llvm.Builder.iCmp, [llvm.IntPredicate.signed_less_than]),
        (ints, "intSmallerOrEqualTo", llvm.Builder.iCmp, [llvm.IntPredicate.signed_less_or_equal_to]),
        (floats, "floatAdd", llvm.Builder.fAdd, []),
        (floats, "floatSub", llvm.Builder.fSub, []),
        (floats, "floatMul", llvm.Builder.fMul, []),
        (floats, "floatDiv", llvm.Builder.fDiv, []),
    ]

    for types, name, instruction, arguments in methods:

        functions = []
        for type in types:
            return_type = bool if arguments else type

            functions.append(
                LLVMFunction("", [type, type], return_type,
                    partial(llvmInstructionWrapper, instruction,
                            additional_arguments=arguments)
                )
            )
        builtin_objects.append(
            lekvar.Method(name, functions)
        )

    builtin_objects.append(
        lekvar.Method("puts",
            [LLVMFunction("", [type], None, partial(llvmPrintfWrapper, type))
            for type in (ints + floats + [string])],
        ),
    )

    return lekvar.Module("_builtins", builtin_objects)

def llvmInstructionWrapper(instruction, self, additional_arguments = []):
    name = resolveName(self)
    func_type = self.type.emitType()
    self.llvm_value = State.module.addFunction(name, func_type)
    entry = self.llvm_value.appendBlock("")

    with State.blockScope(entry):
        lhs = self.llvm_value.getParam(0)
        rhs = self.llvm_value.getParam(1)
        arguments = [State.builder] + additional_arguments + [lhs, rhs, ""]
        return_value = instruction(*arguments)
        State.builder.ret(return_value)

PRINTF_MAP = {
    "String": "s",

    "Int8": "hhd",
    "Int16": "hd",
    "Int32": "d",
    "Int64": "ld",
    "Int128": "lld",

    "Float16": "hg",
    "Float32": "g",
    "Float64": "lg",
}

def llvmPrintfWrapper(type, self):
    global printf
    func_type = llvm.Function.new(llvm.Type.void(), [LLVMType("String").emitType()], True)

    if printf is None:
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
