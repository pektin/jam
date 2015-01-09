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

class Scope(Object):
    verified = False # cache for circular program flows
    parent = None
    children = None

    def __init__(self, children:{str: Object}):
        # set child parents
        for child in children.values():
            if isinstance(child, Scope):
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

class Type(Scope):
    @abstract
    def checkCompatibility(self, other:Type) -> bool:
        pass

    def resolveCompatibility(self, other:Type):
        if not self.checkCompatibility(other):
            raise TypeError("{} is not compatible with {}".format(self.__class__, other.__class__))

class Instruction(ABC):
    @abstract
    def verify(self, scope:Scope):
        pass

#
# Jam Structures
#

class Call(Instruction):
    reference = None
    function = None # resolved through reference

    values = None

    def __init__(self, reference:str, values:[Object]):
        self.reference = reference
        self.values = values

    def verify(self, scope:Scope):
        signature = [value.resolveType() for value in self.values]
        object = scope.resolveReferenceDown(self.reference).resolveType()

        object.resolveCompatibility(FunctionType(signature,[])) # TODO: return types

class Module(Scope):
    main = None

    def __init__(self, children:{str: Object}, main:[Instruction]):
        super().__init__(children)
        self.main = main

    def verify(self):
        super().verify()
        for instruction in self.main:
            instruction.verify(self)

    def resolveType(self):
        #TODO
        raise InternalError("Not yet implemented")

class Literal(Object):
    type = None
    data = None

    def __init__(self, type:Type, data:bytes):
        self.type = type
        self.data = data

    def resolveType(self):
        return self.type

class FunctionType(Type):
    signature = None
    return_types = None

    def __init__(self, signature: [Type], return_types: [Type]):
        self.signature = signature
        self.return_types = return_types

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
            #for self_t, other_t in zip(self.return_types, other.return_types):
            #    if not other_t.checkCompatibility(self_t):
            #        return False
        else:
            return False
        return True

    def resolveType(self):
        raise InternalError("Not implemented")

class Function(Scope):
    arguments = None
    instructions = None
    return_types = None

    def __init__(self, arguments: [(str, Type)], instructions: [Instruction], return_types: [Type]):
        super().__init__({})

        self.arguments = arguments
        self.instructions = instructions
        self.return_types = return_types

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
        return FunctionType([arg[1] for arg in self.arguments], self.return_types)

    def resolveReferenceDown(self, reference:str):
        #TODO (signature stuff)
        return super().resolveReferenceDown(reference)

class ExternalFunction(Function):
    verified = True
    external_name = None

    def __init__(self, external_name:str, arguments: [Type], return_types: [Type]):
        self.external_name = external_name
        self.arguments = arguments
        self.return_types = return_types

    def resolveType(self):
        return FunctionType(self.arguments, self.return_types)

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
