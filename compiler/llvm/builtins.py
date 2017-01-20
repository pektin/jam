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
    size = LLVMType("Int64")
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
    void = lekvar.VoidType("Void")

    builtin_objects = [string, bool, void] + ints + floats

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
        (floats, "floatGreaterThan", llvm.Builder.fCmp, [llvm.RealPredicate.ordered_greater_than]),
        (floats, "floatGreaterOrEqualTo", llvm.Builder.fCmp, [llvm.RealPredicate.ordered_greater_or_equal_to]),
        (floats, "floatSmallerThan", llvm.Builder.fCmp, [llvm.RealPredicate.ordered_less_than]),
        (floats, "floatSmallerOrEqualTo", llvm.Builder.fCmp, [llvm.RealPredicate.ordered_less_or_equal_to]),
    ]

    for types, name, instruction, arguments in methods:

        functions = []
        for type in types:
            return_type = bool if arguments else type

            functions.append(
                LLVMFunction("", [type, type], return_type,
                    partial(llvmInstructionWrapper, instruction,
                            args_before=arguments)
                )
            )
        builtin_objects.append(
            lekvar.Method(name, functions)
        )

    # int -> float conversions
    for int_t in ints:
        for float_t in floats:
            name = int_t.name + "To" + float_t.name
            wrap = partial(llvmInstructionWrapper, llvm.Builder.iToF, args_after=[float_t.emitType()])
            function = LLVMFunction(name, [int_t], float_t, wrap)
            builtin_objects.append(function)

    # float -> int conversions
    for float_t in floats:
        for int_t in ints:
            name = float_t.name + "To" + int_t.name
            wrap = partial(llvmInstructionWrapper, llvm.Builder.fToI, args_after=[int_t.emitType()])
            function = LLVMFunction(name, [float_t], int_t, wrap)
            builtin_objects.append(function)

    builtin_objects.append(
        lekvar.Method("puts",
            [LLVMFunction("", [type], None, partial(llvmPrintfWrapper, type))
            for type in (ints + floats + [string])],
        ),
    )

    builtin_objects.append(lekvar.ExternalFunction("alloc", "calloc", [size], void))
    builtin_objects.append(lekvar.ExternalFunction("free", "free", [void], None))
    builtin_objects.append(lekvar.ExternalFunction("realloc", "realloc", [void, size], void))
    builtin_objects.append(LLVMFunction("ptrOffset", [void, size], void, llvmOffsetWrapper))

    module = lekvar.Module("_builtins", builtin_objects)
    module.verify()
    return module

def llvmInstructionWrapper(instruction, self, args_before = [], args_after = []):
    entry = self.llvm_value.appendBlock("")

    with State.blockScope(entry):
        args = [self.llvm_value.getParam(i) for i in range(len(self.type.arguments))]
        arguments = [State.builder] + args_before + args + args_after + [""]
        return_value = instruction(*arguments)
        State.builder.ret(return_value)

def llvmOffsetWrapper(self):
    entry = self.llvm_value.appendBlock("")

    with State.blockScope(entry):
        ptr = self.llvm_value.getParam(0)
        offset = self.llvm_value.getParam(1)
        result = State.builder.inBoundsGEP(ptr, [offset], "")
        State.builder.ret(result)

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
        self._stats = lekvar.stats.ScopeStats(self.parent)
        self.stats.static = True
        self.stats.forward = False

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
