import sys
import shutil
from ctypes import *
import traceback
import logging

# Set platform specific constants
if sys.platform.startswith("linux"):
    DLL_NAME = "libLLVM-{}.so.1"
elif sys.platform.startswith("darwin"):
    DLL_NAME = "libLLVM-{}.dylib"
else:
    raise OSError("{} is not yet supported".format(sys.platform))

# Load the latest supported llvm version
LLVM_VERSION = '3.6'
try:
    _lib = CDLL(DLL_NAME.format(LLVM_VERSION))
except OSError:
    raise OSError("Failed to load llvm {} Make sure the dll is installed and in the right place.".format(LLVM_VERSION))

def llvm_cmd(cmd, fail_ok = False):
    # First try the version specific command
    path = shutil.which("{}-{}".format(cmd, LLVM_VERSION))
    # Then try without the version
    if path is None:
        path = shutil.which(cmd)

    if path is None and not fail_ok:
        raise OSError("Failed to find required executable: {}".format(cmd))
    return path

LLI = llvm_cmd("lli")
CLANG = llvm_cmd("clang", True)

c_bool = c_int

class NullException(Exception):
    pass

class VerificationError(Exception):
    pass

#
# Wrapping tools
#

# Set the calling convention of a function in _lib
def setTypes(name:str, args:[], ret = None):
    func = getattr(_lib, name)
    func.argtypes = args
    func.restype = ret

# Convert a list of python argument types to a list of C argument types
def convertArgtypes(types):
    arguments = []
    for type in types:
        if isinstance(type, list):
            arguments.append(POINTER(c_void_p))
            arguments.append(c_uint)
        else:
            arguments.append(type)
    return arguments

# Convert python arguments to C arguments. Matches convertArgtypes conversion
def convertArgs(args):
    arguments = []
    for arg in args:
        if isinstance(arg, list):
            arguments.append(cast((c_void_p * len(arg))(*arg), POINTER(c_void_p)))
            arguments.append(len(arg))
        elif isinstance(arg, str):
            arguments.append(arg.encode("UTF-8"))
        else:
            arguments.append(arg)
    return arguments

# Decorator for wrapped C functions that logs any call
def logged(cls_name, name, check_null = True):
    def logged(func):
        def f(self, *args):
            # Log the call, if possible. global State is set by State.begin
            if 'State' in globals() and State.logger and State.logger.isEnabledFor(logging.DEBUG):
                if isinstance(self, type):
                    State.logger.debug("{}.{} calling {}{}".format(
                        self.__name__, cls_name, name, args), stack_info=True)
                else:
                    State.logger.debug("{}.{} calling {}{}".format(
                        self.__class__.__name__, cls_name, name, tuple([self] + list(args))), stack_info=True)

            # Perform the call
            ret = func(self, *args)

            # Check for invalid output
            if check_null and ret is None:
                raise NullException("Binding returned null")

            return ret
        return f
    return logged

class Wrappable:
    @classmethod
    def wrapInstanceFunc(cls, cls_name:str, name:str, args:[] = [], ret = None, check_null = True):
        setTypes(name, convertArgtypes([cls] + args), ret)

        @logged(cls_name, name, check_null and ret is not None)
        def func(self, *args):
            value = getattr(_lib, name)(self, *convertArgs(args))

            # Set debug attributes
            if isinstance(value, Wrappable):
                value.constructor_name = repr(self) + "." + cls_name
                value.constructor_args = args

            return value

        setattr(cls, cls_name, func)

    @classmethod
    def wrapInstanceProp(cls, cls_name:str, get_name:str, set_name:str, type, check_null = True):
        # Create getter
        setTypes(get_name, [cls], type)
        @logged(cls_name, get_name, check_null)
        def get(self):
            value = getattr(_lib, get_name)(self)

            # Set debug attributes
            if isinstance(value, Wrappable):
                value.constructor_name = repr(self) + "." + cls_name

            return value

        # Create Setter
        set = None
        if set_name is not None:
            setTypes(set_name, [cls, type], None)
            @logged(cls_name, set_name, False)
            def set(self, val:type):
                getattr(_lib, set_name)(self, val)

        setattr(cls, cls_name, property(get, set))

    @classmethod
    def wrapDestructor(cls, name:str):
        setTypes(name, [cls], None)
        cls.__del__ = lambda self: getattr(_lib, name)(self)

    @classmethod
    def wrapConstructor(cls, cls_name:str, name:str, args:[] = []):
        setTypes(name, convertArgtypes(args), cls)
        @classmethod
        @logged(cls_name, name)
        def make(cls, *args):
            obj = getattr(_lib, name)(*convertArgs(args))
            # Set debug attributes
            obj.constructor_name = cls.__name__ + "." + cls_name
            obj.constructor_args = args

            return obj
        setattr(cls, cls_name, make)

    # Debugging
    constructor_name = None
    constructor_args = tuple()
    def __repr__(self):
        if self.constructor_name is not None:
            return "{}({})".format(self.constructor_name,
                                   ', '.join(map(str, self.constructor_args)))
        else:
            return Wrappable.__repr__(self)

#
# The Actual LLVM bindings
#

class Context(Wrappable, c_void_p):
    pass

class Module(Wrappable, c_void_p):
    pass

class Builder(Wrappable, c_void_p):
    pass

class Type(Wrappable, c_void_p):
    pass

class Pointer(Type):
    pass

class Int(Type):
    pass

class Float(Type):
    pass

class Function(Type):
    pass

class Struct(Type):
    pass

class Block(Wrappable, c_void_p):
    pass

class Value(Wrappable, c_void_p):
    pass

class FunctionValue(Value):
    pass

class PassManager(Wrappable, c_void_p):
    pass

__all__ = """Context Module Builder Type Pointer Int Float Function Block Value
FunctionValue""".split()


# Error message disposal function
# Internal usage only

setTypes("LLVMDisposeMessage", [c_char_p], None)
disposeError = _lib.LLVMDisposeMessage

#
# Context
#

# Constructors
Context.wrapConstructor("new", "LLVMContextCreate")
Context.wrapConstructor("getGlobal", "LLVMGetGlobalContext")
Context.wrapDestructor("LLVMContextDispose")

#
# Module
#

# Constructors
Module.wrapConstructor("fromName", "LLVMModuleCreateWithName", [c_char_p])
Module.wrapConstructor("fromNameWithContext", "LLVMModuleCreateWithNameInContext", [c_char_p, Context])
Module.wrapDestructor("LLVMDisposeModule")
#clone = Module.wrapInstanceFunc("LLVMCloneModule", [], Module) # Doesn't exist?

# Properties
Module.wrapInstanceProp("data_layout", "LLVMGetDataLayout", "LLVMSetDataLayout", c_char_p)
Module.wrapInstanceProp("target_triple", "LLVMGetTarget", "LLVMSetTarget", c_char_p)
Module.wrapInstanceProp("context", "LLVMGetModuleContext", None, Context)

# Methods
Module.wrapInstanceFunc("dump", "LLVMDumpModule")
Module.wrapInstanceFunc("toString", "LLVMPrintModuleToString", [], c_char_p)
Module.wrapInstanceFunc("getType", "LLVMGetTypeByName", [c_char_p], Type)
Module.wrapInstanceFunc("addFunction", "LLVMAddFunction", [c_char_p, Function], FunctionValue)
Module.wrapInstanceFunc("getFunction", "LLVMGetNamedFunction", [c_char_p], FunctionValue)
Module.wrapInstanceFunc("addVariable", "LLVMAddGlobal", [Type, c_char_p], Value)

setTypes("LLVMVerifyModule", [Module, c_int, POINTER(c_char_p)], c_bool)

@logged("verify", "LLVMVerifyModule", False)
def Module_verify(self):
    error_msg = c_char_p()

    if _lib.LLVMVerifyModule(self, FailureAction.ReturnStatusAction, byref(error_msg)):
        # Convert llvm string to python
        message = "LLVM: \"{}\"\n\nfor:\n{}".format(error_msg.value.decode("UTF-8"), self.toString().decode("UTF-8"))
        disposeError(error_msg)

        raise VerificationError(message)
Module.verify = Module_verify

class FailureAction:
    AbortProcessAction = 0 # verifier will print to stderr and abort()
    PrintMessageAction = 1 # verifier will print to stderr and return 1
    ReturnStatusAction = 2 # verifier will just return 1

#
# Builder
#

# Constructors
Builder.wrapConstructor("new", "LLVMCreateBuilder")
Builder.wrapConstructor("fromContext", "LLVMCreateBuilderInContext", [Context])
Builder.wrapDestructor("LLVMDisposeBuilder")

# Functions
Builder.wrapInstanceFunc("positionAt", "LLVMPositionBuilder", [Block, Value])
Builder.wrapInstanceFunc("positionBefore", "LLVMPositionBuilderBefore", [Value])
Builder.wrapInstanceFunc("positionAtEnd", "LLVMPositionBuilderAtEnd", [Block])
Builder.wrapInstanceProp("position", "LLVMGetInsertBlock", None, Block)

Builder.wrapInstanceFunc("retVoid", "LLVMBuildRetVoid", [], Value)
Builder.wrapInstanceFunc("ret", "LLVMBuildRet", [Value], Value)
#Builder.wrapInstanceFunc("aggregateRet", "LLVMBuildAggregateRet", [[Value]], Value) # Needs a manual wrap

Builder.wrapInstanceFunc("br", "LLVMBuildBr", [Block], Value)
Builder.wrapInstanceFunc("condBr", "LLVMBuildCondBr", [Value, Block, Block], Value)
Builder.wrapInstanceFunc("indirectBr", "LLVMBuildIndirectBr", [Value, c_uint], Value)
Builder.wrapInstanceFunc("destination", "LLVMAddDestination", [Value, Block])
Builder.wrapInstanceFunc("switch", "LLVMBuildSwitch", [Value, Block, c_uint], Value)
Builder.wrapInstanceFunc("case", "LLVMAddCase", [Value, Value, Block])
Builder.wrapInstanceFunc("invoke", "LLVMBuildInvoke", [Value, [Value], Block, Block, c_char_p], Value)

Builder.wrapInstanceFunc("malloc", "LLVMBuildMalloc", [Type, c_char_p], Value)
Builder.wrapInstanceFunc("free", "LLVMBuildFree", [Value], Value)
Builder.wrapInstanceFunc("alloca", "LLVMBuildAlloca", [Type, c_char_p], Value)
Builder.wrapInstanceFunc("load", "LLVMBuildLoad", [Value, c_char_p], Value)
Builder.wrapInstanceFunc("store", "LLVMBuildStore", [Value, Value], Value)

Builder.wrapInstanceFunc("extractValue", "LLVMBuildExtractValue", [Value, c_uint, c_char_p], Value)
Builder.wrapInstanceFunc("insertValue", "LLVMBuildInsertValue", [Value, Value, c_uint, c_char_p], Value)

Builder.wrapInstanceFunc("call", "LLVMBuildCall", [Value, [Value], c_char_p], Value)

Builder.wrapInstanceFunc("cast", "LLVMBuildBitCast", [Value, Type, c_char_p], Value)

Builder.wrapInstanceFunc("iAdd", "LLVMBuildAdd", [Value, Value, c_char_p], Value)
Builder.wrapInstanceFunc("iSub", "LLVMBuildSub", [Value, Value, c_char_p], Value)
Builder.wrapInstanceFunc("iMul", "LLVMBuildMul", [Value, Value, c_char_p], Value)
Builder.wrapInstanceFunc("siDiv", "LLVMBuildSDiv", [Value, Value, c_char_p], Value)
Builder.wrapInstanceFunc("uiDiv", "LLVMBuildUDiv", [Value, Value, c_char_p], Value)
Builder.wrapInstanceFunc("siRem", "LLVMBuildSRem", [Value, Value, c_char_p], Value)
Builder.wrapInstanceFunc("uiRem", "LLVMBuildURem", [Value, Value, c_char_p], Value)

Builder.wrapInstanceFunc("fAdd", "LLVMBuildFAdd", [Value, Value, c_char_p], Value)
Builder.wrapInstanceFunc("fSub", "LLVMBuildFSub", [Value, Value, c_char_p], Value)
Builder.wrapInstanceFunc("fMul", "LLVMBuildFMul", [Value, Value, c_char_p], Value)
Builder.wrapInstanceFunc("fDiv", "LLVMBuildFDiv", [Value, Value, c_char_p], Value)
Builder.wrapInstanceFunc("fRem", "LLVMBuildFRem", [Value, Value, c_char_p], Value)

Builder.wrapInstanceFunc("iCmp", "LLVMBuildICmp", [c_uint, Value, Value, c_char_p], Value)

class IntPredicate:
    equal = 32
    unequal = 33
    unsigned_greater_than = 34
    unsigned_greater_or_equal_to = 35
    unsigned_less_than = 36
    unsigned_less_or_equal_to = 37
    signed_greater_than = 38
    signed_greater_or_equal_to = 39
    signed_less_than = 40
    signed_less_or_equal_to = 41

Builder.wrapInstanceFunc("fCmp", "LLVMBuildFCmp", [c_uint, Value, Value, c_char_p], Value)

class RealPredicate:
    # always_false = 0
    ordered_equal = 1
    ordered_greater_than = 2
    ordered_greter_or_equal_to = 3
    ordered_less_than = 4
    ordered_less_or_equal_to = 5
    ordered_unequal = 6
    ordered = 7
    unordered = 8
    unordered_equal = 9
    unordered_greater_than = 10
    unordered_greter_or_equal_to = 11
    unordered_less_than = 12
    unordered_less_or_equal_to = 13
    unordered_unequal = 14
    # always_true = 15

Builder.wrapInstanceFunc("inBoundsGEP", "LLVMBuildInBoundsGEP", [Value, [Value], c_char_p], Value)
Builder.wrapInstanceFunc("structGEP", "LLVMBuildStructGEP", [Value, c_uint, c_char_p], Value)

Builder.wrapInstanceFunc("globalString", "LLVMBuildGlobalStringPtr", [c_char_p, c_char_p], Value)

#
# Type
#

Type.wrapConstructor("void", "LLVMVoidType")
Type.wrapConstructor("label", "LLVMLabelType")

@staticmethod
def Type_void_p(space = 0):
    return Pointer.new(Int.new(8), space)
Type.void_p = Type_void_p

Type.wrapInstanceProp("context", "LLVMGetTypeContext", None, Context)
Type.wrapInstanceProp("isSized", "LLVMTypeIsSized", None, c_bool)
Type.wrapInstanceProp("kind", "LLVMGetTypeKind", None, c_uint)

class TypeKind:
    VoidTypeKind = 0
    HalfTypeKind = 1
    FloatTypeKind = 2
    DoubleTypeKind = 3
    X86_FP80TypeKind = 4
    FP128TypeKind = 5
    PPC_FP128TypeKind = 6
    LabelTypeKind = 7
    IntegerTypeKind = 8
    FunctionTypeKind = 9
    StructTypeKind = 10
    ArrayTypeKind = 11
    PointerTypeKind = 12
    VectorTypeKind = 13
    MetadataTypeKind = 14
    X86_MMXTypeKind = 15

Type.wrapInstanceFunc("dump", "LLVMDumpType")
Type.wrapInstanceFunc("toString", "LLVMPrintTypeToString", [], c_char_p)

#
# Pointer Types
#

Pointer.wrapConstructor("new", "LLVMPointerType", [Type, c_uint])

Pointer.wrapInstanceProp("address_space", "LLVMGetPointerAddressSpace", None, c_uint)
Pointer.wrapInstanceProp("element_type", "LLVMGetElementType", None, Type)

#
# Integer Types
#

Int.wrapConstructor("new", "LLVMIntType", [c_uint])
Int.wrapInstanceProp("size", "LLVMGetIntTypeWidth", None, c_uint)

#
# Float Types
#

Float.wrapConstructor("half", "LLVMHalfType")
Float.wrapConstructor("float", "LLVMFloatType")
Float.wrapConstructor("double", "LLVMDoubleType")

#
# Function Types
#

Function.wrapConstructor("new", "LLVMFunctionType", [Type, [Type], c_bool])

Function.wrapInstanceProp("return_type", "LLVMGetReturnType", None, Type)

#
# Struct Types
#

Struct.wrapConstructor("new", "LLVMStructCreateNamed", [Context, c_char_p])
Struct.wrapConstructor("newAnonym", "LLVMStructType", [[Type], c_bool])

Struct.wrapInstanceFunc("setBody", "LLVMStructSetBody", [[Type], c_bool])

#
# Block Types
#

Block.wrapInstanceFunc("asValue", "LLVMBasicBlockAsValue", [], Value)
Block.wrapInstanceFunc("getPrevious", "LLVMGetPreviousBasicBlock", [], Block, check_null=False)
Block.wrapInstanceFunc("getNext", "LLVMGetNextBasicBlock", [], Block, check_null=False)
Block.wrapInstanceFunc("insertBlock", "LLVMInsertBasicBlock", [c_char_p], Block)

Block.wrapInstanceFunc("moveBefore", "LLVMMoveBasicBlockBefore", [Block])
Block.wrapInstanceFunc("moveAfter", "LLVMMoveBasicBlockAfter", [Block])

Block.wrapInstanceProp("firstValue", "LLVMGetFirstInstruction", None, Value)
Block.wrapInstanceProp("lastValue", "LLVMGetLastInstruction", None, Value)

Block.wrapInstanceProp("function", "LLVMGetBasicBlockParent", None, FunctionValue)

#
# Value Types
#

Value.wrapConstructor("constInt", "LLVMConstInt", [Type, c_ulonglong, c_bool])
Value.wrapConstructor("constFloat", "LLVMConstReal", [Type, c_double])
Value.wrapConstructor("null", "LLVMConstNull", [Type])
Value.wrapConstructor("undef", "LLVMGetUndef", [Type])
Value.wrapConstructor("constUnnamedStruct", "LLVMConstStruct", [[Value], c_bool])
Value.wrapConstructor("constStruct", "LLVMConstNamedStruct", [Struct, [Value]])

Value.wrapInstanceFunc("dump", "LLVMDumpValue")
Value.wrapInstanceProp("initializer", "LLVMGetInitializer", "LLVMSetInitializer", Value)
Value.wrapInstanceProp("opcode", "LLVMGetInstructionOpcode", None, c_uint)

class Opcode:
    #Terminator Instructions
    Ret            = 1
    Br             = 2
    Switch         = 3
    IndirectBr     = 4
    Invoke         = 5
    # removed 6 due to API changes
    Unreachable    = 7
    # Standard Binary Operators
    Add            = 8
    FAdd           = 9
    Sub            = 10
    FSub           = 11
    Mul            = 12
    FMul           = 13
    UDiv           = 14
    SDiv           = 15
    FDiv           = 16
    URem           = 17
    SRem           = 18
    FRem           = 19
    # Logical Operators
    Shl            = 20
    LShr           = 21
    AShr           = 22
    And            = 23
    Or             = 24
    Xor            = 25
    # Memory Operators
    Alloca         = 26
    Load           = 27
    Store          = 28
    GetElementPtr  = 29
    # Cast Operators
    Trunc          = 30
    ZExt           = 31
    SExt           = 32
    FPToUI         = 33
    FPToSI         = 34
    UIToFP         = 35
    SIToFP         = 36
    FPTrunc        = 37
    FPExt          = 38
    PtrToInt       = 39
    IntToPtr       = 40
    BitCast        = 41
    AddrSpaceCast  = 60
    # Other Operators
    ICmp           = 42
    FCmp           = 43
    PHI            = 44
    Call           = 45
    Select         = 46
    UserOp1        = 47
    UserOp2        = 48
    VAArg          = 49
    ExtractElement = 50
    InsertElement  = 51
    ShuffleVector  = 52
    ExtractValue   = 53
    InsertValue    = 54
    # Atomic operators
    Fence          = 55
    AtomicCmpXchg  = 56
    AtomicRMW      = 57
    # Exception Handling Operators
    Resume         = 58
    LandingPad     = 59

FunctionValue.wrapInstanceFunc("appendBlock", "LLVMAppendBasicBlock", [c_char_p], Block)
FunctionValue.wrapInstanceFunc("getLastBlock", "LLVMGetLastBasicBlock", [], Block)
FunctionValue.wrapInstanceFunc("getFirstBlock", "LLVMGetFirstBasicBlock", [], Block)
FunctionValue.wrapInstanceFunc("getParam", "LLVMGetParam", [c_uint], Value)

FunctionValue.wrapInstanceFunc("addAttr", "LLVMAddFunctionAttr", [c_uint])
FunctionValue.wrapInstanceFunc("getAttr", "LLVMGetFunctionAttr", [], c_uint)
FunctionValue.wrapInstanceFunc("delAttr", "LLVMRemoveFunctionAttr", [c_uint])

class AttributeKind:
    ZExt            = 1 << 0
    SExt            = 1 << 1
    NoReturn        = 1 << 2
    InReg           = 1 << 3
    StructRet       = 1 << 4
    NoUnwind        = 1 << 5
    NoAlias         = 1 << 6
    ByVal           = 1 << 7
    Nest            = 1 << 8
    ReadNone        = 1 << 9
    ReadOnly        = 1 << 10
    NoInline        = 1 << 11
    AlwaysInline    = 1 << 12
    OptimizeForSize = 1 << 13
    StackProtect    = 1 << 14
    StackProtectReq = 1 << 15
    Alignment       = 31<< 16 # WTF? (Taken from LLVM C api)
    NoCapture       = 1 << 21
    NoRedZone       = 1 << 22
    NoImplicitFloat = 1 << 23
    Naked           = 1 << 24
    InlineHint      = 1 << 25
    StackAlignment  = 7 << 26 # WTF?
    ReturnsTwice    = 1 << 29
    UWTable         = 1 << 30
    NonLazyBind     = 1 << 31

# Dirty hack. For some reason setting `type` on FunctionValue overrides
# that on Value, but not the other way around
FunctionValue.wrapInstanceProp("type", "LLVMTypeOf", None, Function)
Value.wrapInstanceProp("type", "LLVMTypeOf", None, Type)

#
# Passes
#

PassManager.wrapConstructor("new", "LLVMCreatePassManager")
PassManager.wrapDestructor("LLVMDisposePassManager")

PassManager.wrapInstanceFunc("run", "LLVMRunPassManager", [Module], c_bool)

setTypes("LLVMPassManagerBuilderCreate", [], c_void_p)
setTypes("LLVMPassManagerBuilderDispose", [c_void_p])
setTypes("LLVMPassManagerBuilderSetOptLevel", [c_void_p, c_uint])
setTypes("LLVMPassManagerBuilderSetSizeLevel", [c_void_p, c_uint])
setTypes("LLVMPassManagerBuilderPopulateModulePassManager", [c_void_p, PassManager])

@logged("setOptLevel", "LLVMPassManagerBuilderSetOptLevel", False)
def PassManager_setOptLevel(self, level:int):
    builder = _lib.LLVMPassManagerBuilderCreate()
    _lib.LLVMPassManagerBuilderSetOptLevel(builder, level)
    _lib.LLVMPassManagerBuilderPopulateModulePassManager(builder, self)
    _lib.LLVMPassManagerBuilderDispose(builder)
PassManager.setOptLevel = PassManager_setOptLevel

@logged("setOptSizeLevel", "LLVMPassManagerBuilderSetSizeLevel", False)
def PassManager_setOptSizeLevel(self, level:int):
    builder = _lib.LLVMPassManagerBuilderCreate()
    _lib.LLVMPassManagerBuilderSetSizeLevel(builder, level)
    _lib.LLVMPassManagerBuilderPopulateModulePassManager(builder, self)
    _lib.LLVMPassManagerBuilderDispose(builder)
PassManager.setOptSizeLevel = PassManager_setOptSizeLevel
