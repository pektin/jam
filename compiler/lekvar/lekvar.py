from .errors import *
from abc import abstractmethod as abstract, ABC

# Python predefines
Type = None
MethodSignature = None

#
# Abstract Base Structures
#

class Object(ABC):
    @abstract
    def resolveType(self) -> Type:
        pass

    @abstract
    def emit(self, emitter):
        pass

class Scope(Object):
    verified = False # cache for circular program flows

    name = None
    parent = None
    children = None

    emit_data = None

    def __init__(self, children:{str: Object}):
        # set child parents
        for name, child in children.items():
            if isinstance(child, Scope):
                child.name = name
                child.parent = self
        self.children = children

    def verify(self) -> None:
        if self.verified: return
        self.verified = True

        for child in self.children.values():
            child.verify()

    def resolveReferenceDown(self, reference:str) -> Object:
        return self._resolveReference(reference)

    def resolveReferenceUp(self, reference:str) -> Object:
        return self._resolveReference(reference)

    def _resolveReference(self, reference:str) -> Object:
        # check local
        obj = self.children.get(reference, None)
        # check parent
        parent_obj = self.parent.resolveReferenceDown(reference) if self.parent else None

        if obj is None:
            if parent_obj is None:
                raise ReferenceError("Missing reference to {}".format(reference))
            else:
                return parent_obj
        else:
            if parent_obj is not None:
                raise ReferenceError("Ambiguous reference to {}".format(reference))
            else:
                return obj

    @abstract
    def emitDefinition(self, emitter):
        pass

class Type(Scope):
    @abstract
    def checkCompatibility(self, other:Type) -> bool:
        pass

    def resolveCompatibility(self, other:Type):
        if not self.checkCompatibility(other):
            raise TypeError("{} is not compatible with {}".format(self.__class__, other.__class__))

#
# Jam Structures
#

class Call(Object):
    reference = None
    called = None # resolved through reference

    values = None

    def __init__(self, reference:str, values:[Object]):
        self.reference = reference
        self.values = values

    def verify(self, scope:Scope):
        signature = [value.resolveType() for value in self.values]
        self.called = scope.resolveReferenceDown(self.reference)

        self.called.resolveType().resolveCompatibility(FunctionType(signature, []))

    def resolveType(self):
        return None

    def emit(self, emitter):
        emitter.emitCall(self) #TODO: Proper Emission

class Literal(Object):
    type = None
    data = None
    emit_data = None

    def __init__(self, type:Type, data:bytes):
        self.type = type
        self.data = data

    def resolveType(self):
        return self.type

    def emit(self, emitter):
        emitter.emitLiteral(self) #TODO: Proper Emission

class FunctionType(Type):
    signature = None
    return_type = None

    def __init__(self, signature: [Type], return_type:Type):
        self.signature = signature
        self.return_type = return_type

    def checkCompatibility(self, other:Type):
        if isinstance(other, FunctionType):
            # check if signature is compatible
            if len(self.signature) != len(other.signature):
                return False
            for self_t, other_t in zip(self.signature, other.signature):
                if not self_t.checkCompatibility(other_t):
                    return False

            #TODO: Return types
            # same check with return types
            # if not other_t.checkCompatibility(self_t):
            #     return False
        else:
            return False
        return True

    def resolveType(self):
        raise InternalError("Not implemented")

    def emit(self, emitter):
        raise InternalError("Not implemented")

    def emitDefinition(self):
        raise InternalError("Not implemented")

class Function(Scope):
    arguments = None
    instructions = None
    return_type = None

    def __init__(self, arguments: [(str, Type)], instructions: [Object], return_type: Type):
        super().__init__({})

        self.arguments = arguments
        self.instructions = instructions
        self.return_type = return_type

        #TODO: Replace unknown types with temps
        for argument in self.arguments:
            if argument[1] is None:
                raise InternalError("Function argument type inference is not yet supported")

    def verify(self):
        if self.verified: return
        self.verified = True

        for instruction in self.instructions:
            instruction.verify(self)

    def resolveType(self):
        return FunctionType([arg[1] for arg in self.arguments], self.return_type)

    def resolveReferenceDown(self, reference:str):
        #TODO (signature stuff)
        return super().resolveReferenceDown(reference)

    def emit(self, emitter):
        if self.emit_data is None:
            self.emitDefinition(emitter)
        emitter.emitFunctionValue(self)

    def emitDefinition(self, emitter):
        if self.emit_data is not None: return

        with emitter.emitFunction(self) as self.emit_data:
            for instruction in self.instructions:
                instruction.emit(emitter)
        print(self.emit_data)

class ExternalFunction(Function):
    verified = True
    external_name = None

    def __init__(self, external_name:str, arguments: [Type], return_type: Type):
        self.external_name = external_name
        self.arguments = arguments
        self.return_type = return_type

    def resolveType(self):
        return FunctionType(self.arguments, self.return_type)

    def emit(self, emitter):
        if self.emit_data is None:
            self.emitDefinition(emitter)
        emitter.emitFunctionValue(self)

    def emitDefinition(self, emitter):
        if self.emit_data is None:
            self.emit_data = emitter.emitExternalFunction(self)

class Module(Scope):
    main = None

    def __init__(self, children:{str: Object}, main:Function):
        super().__init__(children)
        self.main = main
        self.main.parent = self

    def verify(self):
        super().verify()
        self.main.verify()

    def resolveType(self):
        #TODO
        raise InternalError("Not yet implemented")

    def emit(self, emitter):
        raise InternalError("Not yet implemented")

    def emitDefinition(self, emitter):
        self.emit_data = '\0'
        self.main.emitDefinition(emitter)
        emitter.addMain(self.main)

        for child in self.children.values():
            child.emitDefinition(emitter)

#
# Temporary Structures
#

class LLVMType(Type): # Temporary until stdlib is implemented
    verified = True
    llvm_type = None

    def __init__(self, llvm_type:str):
        self.llvm_type = llvm_type

    def __repr__(self):
        return "LLVM:{}".format(self.llvm_type)

    def checkCompatibility(self, other:Type) -> bool:
        if not isinstance(other, LLVMType):
            return False
        if other.llvm_type != self.llvm_type:
            return False
        return True

    def resolveType(self):
        raise InternalError("Not implemented yet")

    def emit(self, emitter):
        emitter.emitLLVMType(self)

    def emitDefinition(self, emitter):
        pass
