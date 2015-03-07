import logging
from abc import abstractmethod as abstract, ABC

from ..errors import *

# Python predefines
Object = None
Scope = None
Variable = None
Module = None
Function = None
FunctionType = None
Type = None

#
# Infrastructure
#

#shared
builtins = logger = None

def verify(module:Module, builtin:Module, log:logging.Logger = None):
    global builtins, logger
    builtins = builtin
    if log is None: logger = logging.getLogger()


    module.verify()

def resolveReference(scope:Object, reference:str):
    found = []

    def getattrs(scope):
        attrs = scope.collectAttributes(scope)
        if reference in attrs:
            attrs.append(attrs[reference])

    # If the object is a scope, resolve up the tree
    getattrs(scope)
    if isinstance(object, Scope):
        while scope.parent is not None:
            scope = scope.parent
            getattrs(scope)

    # Check for reference in builtins
    getattrs(builtins)

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
    def verify(self, scope:Scope):
        pass

    @abstract
    def resolveType(self, scope:Scope):
        pass

    def collectAttributes(self, scope:Scope) -> {str: Object}:
        return self.resolveType(scope).collectAttributes()

    def __repr__(self):
        return "{}:{}".format(self.__class__.__name__, self.resolveType())

class Scope(Object):
    name = None
    parent = None
    verified = False

    def __init__(self, name):
        self.name = name

    @abstract
    def verify(self, scope:Scope = None):
        pass

    @abstract
    def resolveType(self, scope:Scope = None):
        pass

    def collectAttributes(self, scope:Scope = None):
        return super().collectAttributes(None)

    def __repr__(self):
        return "{}({}):{}".format(self.__class__.__name__, self.name, self.resolveType())

class Type(Scope):
    @abstract
    def collectAttributes(self, scope:Scope) -> {str: Object}:
        pass

    @abstract
    def checkCompatibility(self, other:Type) -> bool:
        pass

    def __repr__(self):
        return "{}".format(self.__class__.__name__)

#
# Modules
#

class Module(Scope):
    main = None
    type = None

    def __init__(self, name:str, children:{str: Scope}, main:Function):
        super().__init__(name)
        self.main = main
        self.main.parent = self
        self.type = ModuleType(name,children)

    def verify(self, scope:Scope = None):
        logger.debug(self)

        self.main.verify(self)

    def resolveType(self, scope:Scope = None):
        return self.type

    def __repr__(self):
        return "{}({})<{}>{{{}}}".format(self.__class__.__name__, self.name,
            self.main, ", ".join(repr(child) for child in self.children))

class ModuleType(Type):
    def __init__(self, name:str, children:{str: Scope}):
        super().__init__(name)
        self.children = children

    def verify(self):
        pass

    def collectAttributes(self, scope:Scope = None):
        return self.children

    def checkCompatibility(self, other:Type):
        raise InternalError("Not implemented")

    def resolveType(self, scope:Scope):
        raise InternalError("Not implemented")

#
# Functions
#

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

    def verify(self, scope:Scope):
        logger.debug(self)

        if self.verified: return
        self.verified = True

        returned = False

        for instruction in self.instructions:
            if isinstance(instruction, Return):
                returned = True
            instruction.verify(self)

        if not returned and self.return_type is not None:
            raise SemanticError("One or more function paths do not return")

    def resolveType(self, scope:Scope = None):
        return FunctionType([arg.type for arg in self.arguments], self.return_type)

    def resolveCall(self, other_signature:FunctionType):
        self_signature = self.resolveType()
        if not self_signature.checkCompatibility(other_signature):
            raise TypeError("Function signature {} is not compatible with {}".format(self_signature, other_signature))
        return self

    def __repr__(self):
        return "{}({}):{}({}){{{}}}".format(self.__class__.__name__, self.name, self.resolveType(),
            ", ".join(repr(argument) for argument in self.arguments),
            ", ".join(repr(instruction) for instruction in self.instructions))

class FunctionType(Type):
    signature = None
    return_type = None

    def __init__(self, signature: [Type], return_type:Type):
        self.signature = signature
        self.return_type = return_type

    def verify(self, scope:Scope = None):
        pass

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

    def collectAttributes(self, scope:Scope = None):
        raise InternalError("Not implemented")

    def resolveType(self, scope:Scope = None):
        raise InternalError("Not implemented")

    def __repr__(self):
        return "{}({}):{}".format(self.__class__.__name__, ", ".join(repr(type) for type in self.signature), self.return_type)






#
#TODO: Make tests pass
#

class Reference(Type):
    def __init__(self, reference:str):
        self.reference = reference
        self.value = None

    def verify(self, scope:Scope):
        logger.debug(self)

        self.value = resolveReference(scope, self.reference)
        self.value.verify(scope)

    def resolveType(self, scope:Scope):
        return self.value.resolveType(scope)

    def collectAttributes(self, scope:Scope, reference:str):
        return self.value.collectAttributes(scope, reference)

    def checkCompatibility(self, other:Type) -> bool:
        return self.value.checkCompatibility(other)

    def __repr__(self):
        return "{}({})<{}>".format(self.__class__.__name__, self.reference, self.value)

class Instruction(Object):
    def resolveType(self, scope:Scope):
        return None

    def collectAttributes(self, scope:Scope, reference:str):
        raise InternalError("Cannot collect attributes of instructions")

class Comment(Instruction):
    contents = None

    def __init__(self, contents):
        self.contents = contents

    def verify(self, scope:Scope):
        logger.debug(self)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.contents)

class Assignment(Instruction):
    reference = None
    variable = None # resolved through reference

    value = None

    def __init__(self, reference:str, value:Object):
        self.reference = reference
        self.value = value

    def verify(self, scope:Scope):
        logger.debug(self)

        try:
            self.variable = resolveReference(scope, self.reference)
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

    def __repr__(self):
        return "{}<{}({}) := {}>".format(self.__class__.__name__, self.reference, self.variable, self.value)

class Variable(Scope):
    def __init__(self, name:str, type:Type=None):
        super().__init__(name)
        self.type = type

    def verify(self, scope:Scope = None):
        logger.debug(self)

    def resolveType(self, scope:Scope):
        return self.type

    def copy(self):
        return Variable(self.name, self.type)

class Call(Object):
    called = None
    values = None

    def __init__(self, called:Object, values:[Object]):
        self.values = values
        self.called = called

    def verify(self, scope:Scope):
        logger.debug(self)

        # Pass on verification
        self.called.verify(scope)
        for value in self.values:
            value.verify(scope)

        # Resolve types
        signature = [value.resolveType(scope) for value in self.values]
        self_type = FunctionType(signature, None)
        called_type = self.called.resolveType(scope)

        # Check for type compatibility
        called_type.checkCompatibility(self_type)

    def resolveType(self, scope:Scope):
        return self.called.return_type

    def __repr__(self):
        return "{}<{}>{{{}}}".format(self.__class__.__name__,
            self.called, ", ".join(repr(value) for value in self.values))

class Return(Instruction):
    value = None
    parent = None

    def __init__(self, value:Object):
        self.value = value

    def verify(self, scope:Scope):
        logger.debug(self)

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

    def resolveType(self, scope:Scope):
        return None

    def __repr__(self):
        return "{}<{}>".format(self.__class__.__name__, self.value)

class Literal(Object):
    type = None
    data = None

    def __init__(self, data:bytes, type:Type):
        self.type = type
        self.data = data

    def verify(self, scope:Scope):
        logger.debug(self)
        # Literals are always verified

    def resolveType(self, scope:Scope):
        return self.type

    def __repr__(self):
        return "{}({}):{}".format(self.__class__.__name__, self.data, self.type)

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

    def verify(self, scope:Scope = None):
        pass

    def resolveType(self, scope:Scope = None):
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

    def resolveType(self, scope:Scope):
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

    def verify(self, scope:Scope):
        logger.debug(self)

        if self.verified: return
        self.verified = True

        for overload in self.overloads:
            overload.verify(scope)

    def resolveType(self, scope:Scope):
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
