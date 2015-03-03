from ctypes import *

_lib = CDLL("/usr/lib/llvm-3.6/lib/libLLVM-3.6.so") #TODO: Do this properly

c_bool = c_int

#
# Wrapping tools
#

def setTypes(name:str, args:[], ret):
    func = getattr(_lib, name)
    func.argtypes = args
    func.restype = ret

def check(func):
    def f(*args):
        res = func(*args)
        if not res:
            raise Exception("{} failed with {}".format(func, res))
    return f

def convertArgtypes(types):
    arguments = []
    for type in types:
        if isinstance(type, list):
            arguments.append(POINTER(c_void_p))
            arguments.append(c_uint)
        else:
            arguments.append(type)
    return arguments

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

class Wrappable:
    @classmethod
    def wrapInstanceFunc(cls, cls_name:str, name:str, args:[] = [], ret = None):
        setTypes(name, convertArgtypes([cls] + args), ret)
        if ret is None:
            def func(self, *args):
                getattr(_lib, name)(self, *convertArgs(args))
        else:
            def func(self, *args):
                return getattr(_lib, name)(self, *convertArgs(args))
        setattr(cls, cls_name, func)

    @classmethod
    def wrapInstanceProp(cls, cls_name:str, get_name:str, set_name:str, type):
        setTypes(get_name, [cls], type)
        @property
        def get(self):
            return getattr(_lib, get_name)(self)
        if set_name:
            setTypes(set_name, [cls, type], None)
            @get.setter
            def set(self, val:type):
                getattr(_lib, set_name)(self, val)
        setattr(cls, cls_name, get)

    @classmethod
    def wrapDestructor(cls, name:str):
        setTypes(name, [cls], None)
        cls.__del__ = lambda self: getattr(_lib, name)(self)

    @classmethod
    def wrapConstructor(cls, cls_name:str, name:str, args:[] = []):
        setTypes(name, convertArgtypes(args), cls)
        @classmethod
        def make(cls, *args):
            return getattr(_lib, name)(*convertArgs(args))
        setattr(cls, cls_name, make)

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

class Block(Wrappable, c_void_p):
    pass

class Value(Wrappable, c_void_p):
    pass

class FunctionValue(Value):
    pass

__all__ = "Context Module Builder Type Pointer Int Float Function Block Value FunctionValue".split()

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

#
# Builder
#

# Constructors
Builder.wrapConstructor("new", "LLVMCreateBuilder")
Builder.wrapConstructor("withContext", "LLVMCreateBuilderInContext", [Context])
Builder.wrapDestructor("LLVMDisposeBuilder")

# Functions
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
Builder.wrapInstanceFunc("invoke", "LLVMBuildInvoke", [Value, [Value], Block, Block, c_char_p], Value) # ditto

Builder.wrapInstanceFunc("malloc", "LLVMBuildMalloc", [Type, c_char_p], Value)
Builder.wrapInstanceFunc("free", "LLVMBuildFree", [Value], Value)
Builder.wrapInstanceFunc("alloca", "LLVMBuildAlloca", [Type, c_char_p], Value)
Builder.wrapInstanceFunc("load", "LLVMBuildLoad", [Value, c_char_p], Value)
Builder.wrapInstanceFunc("store", "LLVMBuildStore", [Value, Value], Value)

Builder.wrapInstanceFunc("call", "LLVMBuildCall", [FunctionValue, [Value], c_char_p], Value)

Builder.wrapInstanceFunc("globalString", "LLVMBuildGlobalStringPtr", [c_char_p, c_char_p], Value)

#
# Type
#

Type.wrapConstructor("void", "LLVMVoidType")
Type.wrapConstructor("label", "LLVMLabelType")

Type.wrapInstanceProp("context", "LLVMGetTypeContext", None, Context)
Type.wrapInstanceProp("isSized", "LLVMTypeIsSized", None, c_bool)

Type.wrapInstanceFunc("dump", "LLVMDumpType")
Type.wrapInstanceFunc("__str__", "LLVMPrintTypeToString", [], c_char_p)

#
# Pointer Types
#

Pointer.wrapConstructor("new", "LLVMPointerType", [Type, c_uint])

Pointer.wrapInstanceProp("address_space", "LLVMGetPointerAddressSpace", None, c_uint)

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

#
# Block Types
#

Block.wrapInstanceFunc("asValue", "LLVMBasicBlockAsValue", [], Value)

#
# Value Types
#

Value.wrapConstructor("constInt", "LLVMConstInt", [Type, c_ulonglong, c_bool])

Value.wrapInstanceProp("type", "LLVMTypeOf", None, Type)
Value.wrapInstanceFunc("dump", "LLVMDumpValue")

FunctionValue.wrapInstanceFunc("appendBlock", "LLVMAppendBasicBlock", [c_char_p], Block)
FunctionValue.wrapInstanceFunc("getLastBlock", "LLVMGetLastBasicBlock", [], Block)
FunctionValue.wrapInstanceFunc("getParam", "LLVMGetParam", [c_uint], Value)
