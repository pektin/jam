import logging
from abc import abstractmethod as abstract, ABC

from ..errors import *

# Python predefines
Object = None
Scope = None
Type = None
Module = None
Function = None
FunctionType = None

#
# Infrastructure
#

def verify(module:Module, builtins:Module, logger:logging.Logger = None):
    if logger is None: logger = logging.getLogger()

    module.verify(State(builtins, logger))

class State:
    def __init__(self, builtins:Module, logger:logging.Logger):
        self.builtins = builtins
        self.logger = logger

def resolveReference(scope:Object, state:State, object:Object, reference:str):
    attrs = object.collectAttributes(scope, state, reference)

    # If the object is a scope, resolve up the tree
    if isinstance(object, Scope):
        while object.parent is not None:
            object = object.parent
            attrs += object.collectAttributes(scope, state, reference)

    if len(attrs) < 1:
        raise MissingReferenceError("No reference to {}".format(reference))
    elif len(attrs) > 1:
        raise AmbiguetyError("Ambiguous reference to {}".format(reference))

    return attrs[0]

#
# Abstract Base Structures
#

class Object(ABC):
    @abstract
    def verify(self, scope:Scope, state:State):
        pass

    @abstract
    def resolveType(self, scope:Scope, state:State):
        pass

    def collectAttributes(scope:Scope, state:State, reference:str) -> [Object]:
        return self.resolveType(scope, state).collectAttributes(state, reference)

    def __repr__(self):
        return "{}:{}".format(self.__class__.__name__, self.resolveType())

class Scope(Object):
    name = None
    parent = None

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "{}({}):{}".format(self.__class__.__name__, self.name, self.resolveType())

class Type(Scope):
    @abstract
    def collectAttributes(self, state:State, reference:str) -> [Object]:
        pass

    @abstract
    def checkCompatibility(self, other:Type) -> bool:
        pass

    def __repr__(self):
        return "{}".format(self.__class__.__name__)

#
# Jam Structures
#

class Comment(Object):
    contents = None

    def __init__(self, contents):
        self.contents = contents

    def verify(self, scope:Scope, state:State):
        state.logger.debug(self)

    def resolveType(self):
        return None

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.contents)

class Assignment(Object):
    reference = None
    variable = None # resolved through reference

    value = None

    def __init__(self, reference:str, value:Object):
        self.reference = reference
        self.value = value

    def verify(self, scope:Scope, state:State):
        state.logger.debug(self)

        try:
            self.variable = scope.resolveReferenceDown(self.reference, state)
        except MissingReferenceError:
            self.variable = Variable(self.reference)
            scope.addChild(self.variable)

        if not isinstance(self.variable, Variable):
            raise TypeError("Cannot assign to {}".format(self.variable))

        # Resolve type compatibility
        self.value.verify(scope, state)
        value_type = self.value.resolveType()
        if self.variable.type is None:
            self.variable.type = value_type
        else:
            self.variable.type.resolveCompatibility(value_type)

    def resolveType(self):
        return None

    def __repr__(self):
        return "{}<{}({}) := {}>".format(self.__class__.__name__, self.reference, self.variable, self.value)

class Variable(ScopeObject):
    type = None

    def __init__(self, name:str, type:Type=None):
        super().__init__(name)
        self.type = type

    def verify(self, scope:Scope, state:State):
        state.logger.debug(self)

    def resolveType(self):
        return self.type

    def copy(self):
        return Variable(self.name, self.type)

class Reference(Object):
    reference = None
    value = None # resolved through reference

    def __init__(self, reference:str):
        self.reference = reference

    def verify(self, scope:Scope, state:State):
        state.logger.debug(self)

        self.value = scope.resolveReferenceDown(self.reference, state)
        self.value.verify(scope, state)

    def resolveType(self):
        return self.value.resolveType()

    def __repr__(self):
        return "{}({})<{}>".format(self.__class__.__name__, self.reference, self.value)

class Call(Object):
    reference = None
    called = None # resolved through reference

    values = None

    def __init__(self, reference:str, values:[Object], called:Function = None):
        self.reference = reference
        self.values = values
        self.called = called

    def verify(self, scope:Scope, state:State):
        state.logger.debug(self)

        if self.called is not None: return
        # Pass on verification to contained values
        for value in self.values: value.verify(scope, state)
        # Verify signature
        signature = [value.resolveType() for value in self.values]
        self.called = scope.resolveReferenceDown(self.reference, state)

        self.called = self.called.resolveCall(FunctionType(signature, []))

    def resolveType(self):
        return self.called.return_type

    def __repr__(self):
        return "{}({})<{}>{{{}}}".format(self.__class__.__name__, self.reference,
            self.called, ", ".join(repr(value) for value in self.values))

class Return(Object):
    value = None
    parent = None

    def __init__(self, value:Object):
        self.value = value

    def verify(self, scope:Scope, state:State):
        state.logger.debug(self)

        # Pass on verification
        self.value.verify(scope, state)

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

    def __repr__(self):
        return "{}<{}>".format(self.__class__.__name__, self.value)

class Literal(Object):
    type = None
    data = None

    def __init__(self, data:bytes, type:Type):
        self.type = type
        self.data = data

    def verify(self, scope, state:State):
        state.logger.debug(self)
        # Literals are always verified

    def resolveType(self):
        return self.type

    def __repr__(self):
        return "{}({}):{}".format(self.__class__.__name__, self.data, self.type)

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
        return "{}({}):{}".format(self.__class__.__name__, ", ".join(repr(type) for type in self.signature), self.return_type)

class Function(Scope):
    arguments = None
    instructions = None
    return_type = None

    def __init__(self, name:str, arguments: [Variable], instructions: [Object], return_type: Type = None):
        super().__init__(name)

        self.arguments = arguments
        self.instructions = instructions
        self.return_type = return_type

        #TODO: Replace unknown types with temps
        for argument in self.arguments:
            if argument.type is None:
                raise InternalError("Function argument type inference is not yet supported")

    def verify(self, state:State):
        state.logger.debug(self)

        if self.verified: return
        self.verified = True

        returned = False

        for instruction in self.instructions:
            if isinstance(instruction, Return):
                returned = True
            instruction.verify(self, state)

        if not returned and self.return_type is not None:
            raise SemanticError("One or more function paths do not return")

    def resolveType(self):
        return FunctionType([arg.type for arg in self.arguments], self.return_type)

    def resolveCall(self, other_signature:FunctionType):
        self_signature = self.resolveType()
        if not self_signature.checkCompatibility(other_signature):
            raise TypeError("Function signature {} is not compatible with {}".format(self_signature, other_signature))
        return self

    def collectReferencesDown(self, reference:str, state:State):
        objects = super().collectReferencesDown(reference, state)
        # Find any references in the function arguments
        for argument in self.arguments:
            if argument.name == reference:
                objects.append(argument)
        return objects

    def __repr__(self):
        return "{}({}):{}({}){{{}}}".format(self.__class__.__name__, self.name, self.resolveType(),
            ", ".join(repr(argument) for argument in self.arguments),
            ", ".join(repr(instruction) for instruction in self.instructions))

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

    def __repr__(self):
        return "{}({} -> {}):{}".format(self.__class__.__name__, self.name, self.external_name, self.resolveType())

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

    def assimilate(self, method):
        self.overloads += method.overloads

    def verify(self, state:State):
        state.logger.debug(self)

        if self.verified: return
        self.verified = True

        for overload in self.overloads:
            overload.verify(state)

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

    def __repr__(self):
        return "{}({}){{{}}}".format(self.__class__.__name__, self.name,
            ", ".join(repr(overload) for overload in self.overloads))

class Module(Scope):
    main = None

    def __init__(self, name:str, children:{str: ScopeObject}, main:Function):
        super().__init__(name, children)
        self.main = main
        self.main.parent = self

    def verify(self, state:State):
        state.logger.debug(self)

        super().verify(state)
        self.main.verify(state)

    def resolveType(self):
        #TODO
        raise InternalError("Not yet implemented")

    def __repr__(self):
        return "{}({})<{}>{{{}}}".format(self.__class__.__name__, self.name,
            self.main, ", ".join(repr(child) for child in self.children))

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

    def __repr__(self):
        return "{}<{}>".format(self.__class__.__name__, self.llvm_type)

class Builtins(Module):
    def __init__(self, children):
        super().__init__("builtins", children, Function([], [], None))

    def collectReferencesDown(self, reference:str, state):
        obj = self.children.get(reference, None)
        if obj is not None:
            return [obj]
        return []

