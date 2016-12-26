import logging
from functools import partial

from .state import State
from .util import *
from .. import lekvar
from . import bindings as llvm

def builtins(logger = logging.getLogger()):
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
        (ints, "intRem", llvm.Builder.siRem, []),
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
        (floats, "floatRem", llvm.Builder.fRem, []),
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

    module = lekvar.Module("_builtins", builtin_objects)
    module.verify()
    return module

def llvmInstructionWrapper(instruction, self, additional_arguments = []):
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

    if printf is None:
        func_type = llvm.Function.new(LLVMType("Int32").emitType(), [LLVMType("String").emitType()], True)
        printf = State.module.addFunction("printf", func_type)
    entry = self.llvm_value.appendBlock("")

    with State.blockScope(entry):
        fmt_str_data = "%{}\n".format(PRINTF_MAP[type.name])
        fmt_string = State.builder.globalString(fmt_str_data, "")

        value = self.llvm_value.getParam(0)

        State.builder.call(printf, [fmt_string, value], "")
        State.builder.retVoid()

#
# Temporary
#

class LLVMType(lekvar.Type, lekvar.BoundObject):
    def __init__(self, name:str):
        lekvar.BoundObject.__init__(self, name)

    def verify(self):
        pass

    def resolveType(self):
        raise InternalError("LLVMTypes are typeless")

    @property
    def local_context(self):
        raise InternalError("LLVMTypes do not have a local context")

    def checkCompatibility(self, other:lekvar.Type, check_cache = None):
        other = other.resolveValue()

        if isinstance(other, LLVMType):
            if self.name == other.name:
                return True
        return False

    def __repr__(self):
        return "{}<{}>".format(self.__class__.__name__, self.name)

    # Emission

    LLVM_MAP = None

    def resetLocalEmission(self):
        return None

    def emit(self):
        pass

    def emitType(self):
        if LLVMType.LLVM_MAP is None:
            LLVMType.LLVM_MAP = {
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
        return LLVMType.LLVM_MAP[self.name]

class LLVMFunction(lekvar.ExternalFunction):
    generator = None

    def __init__(self, name:str, arguments:[lekvar.Type], return_type:lekvar.Type, generator):
        lekvar.ExternalFunction.__init__(self, name, name, arguments, return_type)
        self.generator = generator

    @property
    def local_context(self):
        raise InternalError("LLVMFunctions do not have a local context")

    # Emission

    def resetLocalEmission(self):
        return None

    def emit(self):
        if self.llvm_value is None:
            lekvar.ExternalFunction.emit(self)
            self.generator(self)
