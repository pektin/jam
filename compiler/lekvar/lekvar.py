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
    values = None

    def __init__(self, reference:str, values:[Object]):
        self.reference = reference
        self.values = values

    def verify(self, scope:Scope):
        signature = MethodSignature([value.resolveType() for value in self.values])
        method = scope.resolveReferenceDown(self.reference).resolveType()

        if not isinstance(method, MethodType):
            raise TypeError("{} is not callable".format(method.__class__))

        # Check for a matching signature
        for index, methodsig in enumerate(method.signatures):
            if signature.checkCompatibility(methodsig):
                # Lock signature
                method.locks[index] = True
                return
        raise TypeError("No matching signature")



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

class MethodSignature:
    types = None

    def __init__(self, types:[Type]):
        self.types = types

    def checkCompatibility(self, other:MethodSignature):
        if len(self.types) != len(other.types):
            return False
        for type1, type2 in zip(self.types, other.types):
            if not type1.checkCompatibility(type2):
                return False
        return True

class MethodType(Type):
    signatures = None
    locks = None

    def __init__(self, signatures: [MethodSignature]):
        self.signatures = signatures
        self.locks = [False for sig in self.signatures]

    def checkCompatibility(self, other:Type):
        return False #TODO

    def resolveCompatibility(self, other:Type):
        if not isinstance(other, MethodType):
            raise TypeError("Method types are not compatible with {} types".format(other.__class__))
        # check for matching signatures
        index = 0
        while index < len(self.signatures):
            sig = self.signatures[index]

            contains = False
            # find a signature that matches
            for othersig in other.signatures:
                if sig.checkCompatibility(othersig):
                    contains = True
                    break
            # remove signature from type if other type does not contain it
            if not contains:
                if self.locks[index]:
                    raise TypeError("Method does not supply required overloads")
                self.locks.pop(index)
                self.signatures.pop(index)
            else:
                index += 1

        # Sanity check
        if len(self.signatures) == 0:
            raise TypeError("Method type resolves to null")

    def resolveType(self):
        raise InternalError("Not implemented")

class Method(Scope):
    overloads = None

    def __init__(self, overloads: { MethodSignature: [Instruction] }):
        self.overloads = overloads
        super().__init__({})

    def resolveReferenceDown(self, reference:str):
        #TODO (signature stuff)
        super().resolveReferenceDown(reference)

    def resolveType(self):
        signatures = self.overloads.keys()
        return MethodType(signatures)

#
# Temporary Structures
#

class LLVMType(Type): # Temporary until stdlib is implemented
    verified = True
    llvm_type = None

    def __init__(self, llvm_type:str):
        self.llvm_type = llvm_type

    def checkCompatibility(self, other:Type) -> bool:
        if not isinstance(other, LLVMType):
            return False
        if other.llvm_type != self.llvm_type:
            return False
        return True

    def resolveType(self):
        raise InternalError("Not implemented yet")

class ExternalMethod(Method):
    verified = True
