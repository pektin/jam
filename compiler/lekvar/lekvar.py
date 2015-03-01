from ..errors import *
from abc import abstractmethod as abstract, ABC

builtins = None
def verify(module):
    # Create the builtins
    global builtins
    builtins = Builtins({
        "print": ExternalFunction("print", "puts", [LLVMType("String")], LLVMType("Int"))
    })
    module.verify()

# Python predefines
Type = None
Function = None
FunctionType = None

#
# Abstract Base Structures
#

class Object(ABC):
    @abstract
    def resolveType(self) -> Type:
        """ Returns the type of this object.
        Must return an instance of Type or None.
        If the type is None, this object is considered void (side-effects only)
        Otherwise the object can be used as a value.
        """

    def resolveCall(self, signature:FunctionType) -> Function:
        """ Returns a function that matches a call signature for this object.
        Must return either a Function instance or raise a TypeError
        """
        raise TypeError("{} object is not callable".format(self))

    def __repr__(self):
        return "{}<{}>".format(self.__class__.__name__, self.resolveType())

class ScopeObject(Object):
    name = None
    parent = None

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "{}<{}:{}>".format(self.__class__.__name__, self.name, self.resolveType())

class Scope(ScopeObject):
    verified = False # cache for circular program flows

    parent = None
    children = None

    def __init__(self, name, children:{str: ScopeObject} = {}):
        super().__init__(name)

        # set children
        self.children = children
        for child in children.values():
            child.parent = self

    def addChild(self, child:ScopeObject):
        child.parent = self
        self.children[child.name] = child

    def verify(self) -> None:
        if self.verified: return
        self.verified = True

        for child in self.children.values():
            child.verify()

    def resolveReferenceDown(self, reference:str) -> Object:
        objects = self.collectReferencesDown(reference)
        if len(objects) < 1:
            raise MissingReferenceError("Missing reference to {}".format(reference))
        elif len(objects) > 1:
            raise AmbiguetyError("Ambiguous reference to {}".format(reference))
        return objects[0]

    def resolveReferenceUp(self, reference:str) -> Object: #TODO: Make this work
        return self._resolveReference(reference)

    def collectReferencesDown(self, reference:str) -> Object:
        out = []
        # check local
        obj = self.children.get(reference, None)
        if obj is not None:
            out.append(obj)
        # check parent
        more = self.parent.collectReferencesDown(reference) if self.parent else builtins.collectReferencesDown(reference)
        if more is not None:
            out += more
        return out

class Type(Scope):
    @abstract
    def checkCompatibility(self, other:Type) -> bool:
        pass

    def resolveCompatibility(self, other:Type):
        if not self.checkCompatibility(other):
            raise TypeError("{} is not compatible with {}".format(self, other))

    def __repr__(self):
        return "{}".format(self.__class__.__name__)

#
# Jam Structures
#

class Comment(Object):
    contents = None

    def __init__(self, contents):
        self.contents = contents

    def verify(self, scope:Scope):
        pass

    def resolveType(self):
        return None

class Assignment(Object):
    reference = None
    variable = None # resolved through reference

    value = None

    def __init__(self, reference:str, value:Object):
        self.reference = reference
        self.value = value

    def verify(self, scope:Scope):
        try:
            self.variable = scope.resolveReferenceDown(self.reference)
        except MissingReferenceError:
            self.variable = Variable(self.reference)
            scope.addChild(self.variable)

        if not isinstance(self.variable, Variable):
            raise TypeError("Cannot assign to {}".format(self.variable))

        # Resolve type compatibility
        self.value.verify(scope)
        value_type = self.value.resolveType()
        if self.variable.type is None:
            self.variable.type = value_type
        else:
            self.variable.type.resolveCompatibility(value_type)

    def resolveType(self):
        return None

class Variable(ScopeObject):
    type = None

    def __init__(self, name:str, type:Type=None):
        super().__init__(name)
        self.type = type

    def verify(self, scope:Scope):
        pass

    def resolveType(self):
        return self.type

class Reference(Object):
    reference = None
    value = None # resolved through reference

    def __init__(self, reference:str):
        self.reference = reference

    def verify(self, scope:Scope):
        self.value = scope.resolveReferenceDown(self.reference)
        self.value.verify(scope)

    def resolveType(self):
        return self.value.resolveType()

    def __repr__(self):
        return "Reference<{}>".format(self.reference)

class Call(Object):
    reference = None
    called = None # resolved through reference

    values = None

    def __init__(self, reference:str, values:[Object]):
        self.reference = reference
        self.values = values

    def verify(self, scope:Scope):
        # Pass on verification to contained values
        for value in self.values: value.verify(scope)
        # Verify signature
        signature = [value.resolveType() for value in self.values]
        self.called = scope.resolveReferenceDown(self.reference)

        self.called = self.called.resolveCall(FunctionType(signature, []))

    def resolveType(self):
        return self.called.return_type

    def __repr__(self):
        return "Call<{}: {}>".format(self.reference, ", ".join(repr(value) for value in self.values))

class Return(Object):
    value = None
    parent = None

    def __init__(self, value:Object):
        self.value = value

    def verify(self, scope:Scope):
        # Pass on verification
        self.value.verify(scope)

        # Verify signature
        if not isinstance(scope, Function):
            raise SyntaxError("Cannot return outside of a function")
        self.parent = scope

        if scope.return_type is None:
            scope.return_type = self.value.resolveType()
        else:
            scope.return_type.resolveCompatibility(self.value.resolveType())

    def resolveType(self):
        return None

class Literal(Object):
    type = None
    data = None

    def __init__(self, data:bytes, type:Type):
        self.type = type
        self.data = data

    def verify(self, scope):
        pass # Literals are always verified

    def resolveType(self):
        return self.type

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

    def __repr__(self):
        return "(" + ", ".join(repr(type) for type in self.signature) + "):{}".format(self.return_type)

class Function(Scope):
    arguments = None
    instructions = None
    return_type = None

    def __init__(self, name:str, arguments: [Variable], instructions: [Object], return_type: Type = None):
        super().__init__(name)
        self.name = name

        self.arguments = arguments
        self.instructions = instructions
        self.return_type = return_type

        #TODO: Replace unknown types with temps
        for argument in self.arguments:
            if argument.type is None:
                raise InternalError("Function argument type inference is not yet supported")

    def verify(self):
        if self.verified: return
        self.verified = True

        returned = False

        for instruction in self.instructions:
            if isinstance(instruction, Return):
                returned = True
            instruction.verify(self)

        if not returned and self.return_type is not None:
            raise SemanticError("One or more function paths do not return")

    def resolveType(self):
        return FunctionType([arg.type for arg in self.arguments], self.return_type)

    def resolveCall(self, other_signature:FunctionType):
        self_signature = self.resolveType()
        if not self_signature.checkCompatibility(other_signature):
            raise TypeError("Function signature {} is not compatible with {}".format(self_signature, other_signature))
        return self

    def collectReferencesDown(self, reference:str):
        objects = super().collectReferencesDown(reference)
        # Find any references in the function arguments
        for argument in self.arguments:
            if argument.name == reference:
                objects.append(argument)
        return objects

class ExternalFunction(Scope):
    verified = True
    external_name = None
    argument_types = None
    return_type = None

    def __init__(self, name:str, external_name:str, argument_types: [Type], return_type: Type):
        super().__init__(name)
        self.external_name = external_name
        self.argument_types = argument_types
        self.return_type = return_type

    def resolveType(self):
        return FunctionType(self.argument_types, self.return_type)

    resolveCall = Function.resolveCall

class MethodType(Type):
    overloads = None

    def __init__(self, overloads:[FunctionType]):
        self.overloads = overloads

    def checkCompatibility(self, other:Type):
        if isinstance(other, MethodType):
            # sanity check
            if len(self.overloads) == len(other.overloads):
                # Check that there is a match to any overload in the other, for all overloads in this one
                return all(
                    any(self_over.checkCompatibility(other_over) for other_over in other.overloads)
                        for self_over in self.overloads)

    def resolveCompatibility(self, other:Type):
        if isinstance(other, FunctionType):
            for overload in self.overloads:
                if overload.checkCompatibility(other):
                    return
        raise TypeError("{} is not compatible with {}".format(self, other))

    def resolveType(self):
        raise InternalError("Not implemented")

class Method(Scope):
    overloads = None

    def __init__(self, name:str, overloads:[Function]):
        super().__init__(name)

        self.overloads = []
        for overload in overloads:
            self.addOverload(overload)

    def addOverload(self, fn:Function):
        fn.name = str(len(self.overloads))
        fn.parent = self
        self.overloads.append(fn)

    def verify(self):
        if self.verified: return
        self.verified = True

        for overload in self.overloads:
            overload.verify()

    def resolveType(self):
        return MethodType(function.resolveType() for function in self.overloads)

    def resolveCall(self, signature):
        found = []

        for overload in self.overloads:
            overld_sig = overload.resolveType()
            if signature.checkCompatibility(overld_sig):
                found.append(overload)

        if len(found) == 0:
            raise TypeError("No compatible overload found for {}".format(signature))
        elif len(found) > 1:
            raise TypeError("Ambiguous overloads for {}",format(signature))
        return found[0]

class Module(Scope):
    main = None

    def __init__(self, name:str, children:{str: ScopeObject}, main:Function):
        super().__init__(name, children)
        self.main = main
        self.main.parent = self

    def verify(self):
        super().verify()
        self.main.verify()

    def resolveType(self):
        #TODO
        raise InternalError("Not yet implemented")

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

    def __repr__(self):
        return "{}<{}>".format(self.__class__.__name__, self.llvm_type)

class Builtins(Module):
    def __init__(self, children):
        super().__init__("builtins", children, Function([], [], None))

    def collectReferencesDown(self, reference:str):
        obj = self.children.get(reference, None)
        if obj is not None:
            return [obj]
        return []

