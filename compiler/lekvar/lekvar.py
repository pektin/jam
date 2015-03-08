import logging
from abc import abstractmethod as abstract, ABC, abstractproperty

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

    module.verify(None)

def resolveReference(scope:Object, reference:str):
    found = []

    # If the object is a scope, resolve up the tree

    while scope is not None:
        attr = scope.resolveAttribute(reference, scope)
        if attr is not None:
            found.append(attr)
        scope = scope.parent

    # Check for reference in builtins
    attr = builtins.resolveAttribute(reference, scope)
    if attr is not None:
        found.append(attr)

    if len(found) < 1:
        raise MissingReferenceError("No reference to {}".format(reference))
    elif len(found) > 1:
        raise AmbiguetyError("Ambiguous reference to {}".format(reference))

    return found[0]

def ensure_verified(fn):
    def func(self, *args):
        if not self.verified:
            self.verify(self.parent)
        return fn(self, *args)
    return func

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

    def resolveAttribute(self, reference:str, scope:Scope) -> Object:
        attributes = self.resolveType(scope).attributes
        if reference in attributes:
            return attributes[reference]
        return None

    def resolveCall(self, call:FunctionType, scope:Scope) -> Function:
        raise TypeError("{} object is not callable".format(self))

    def __repr__(self):
        return "{}".format(self.__class__.__name__)

class ScopeObject(Object):
    name = None
    parent = None
    verified = False

    def __init__(self, name):
        self.name = name

    @abstract
    def verify(self, scope:Scope):
        self.verified = True

    @abstract
    @ensure_verified
    def resolveType(self, scope:Scope):
        pass

    @ensure_verified
    def resolveAttribute(self, reference:str, scope:Scope):
        return super().resolveAttribute(reference, scope)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.name)

class Scope(ScopeObject):
    def __init__(self, name, children:[ScopeObject] = []):
        super().__init__(name)

        for child in children:
            self.addChild(child)

    def verify(self, scope:Scope):
        super().verify(scope)
        for child in self.children.values():
            child.verify(self)

    @ensure_verified
    def resolveAttribute(self, reference:str, scope:Scope):
        if reference in self.children:
            return self.children[reference]
        return None

    @abstractproperty
    def children(self) -> {str: ScopeObject}:
        pass

    @abstract
    def addChild(self, child:ScopeObject):
        child.parent = self

    def __repr__(self):
        return "{}({}){}".format(self.__class__.__name__, self.name, self.children)

class Type(Scope):
    def __init__(self, name, attributes:[ScopeObject] = []):
        super().__init__(name, attributes)

    @ensure_verified
    def resolveAttribute(self, reference:str, scope:Scope):
        super(ScopeObject).resolveAttribute(reference, scope)

    @abstract
    @ensure_verified
    def checkCompatibility(self, other:Type) -> bool:
        pass


#
# Module
#

class Module(Scope):
    main = None
    _children = None

    def __init__(self, name:str, children:[ScopeObject], main:Function):
        self._children = {}
        super().__init__(name, children)
        self.main = main

    def verify(self, scope:Scope):
        super().verify(scope)
        self.main.verify(self)

    @ensure_verified
    def resolveType(self, scope:Scope):
        raise InternalError("Not Implemented")

    @property
    def children(self):
        return self._children

    def addChild(self, child:ScopeObject):
        super().addChild(child)
        self._children[child.name] = child

    def __repr__(self):
        return "{}({})<{}>{}".format(self.__class__.__name__, self.name, self.main, self.children)

#
# Function
#

class Function(Scope):
    _children = None
    arguments = None
    instructions = None
    type = None

    def __init__(self, name:str, arguments:[Variable], instructions:[Object], return_type:Type):
        self._children = {}
        super().__init__(name, arguments)
        self.arguments = arguments
        self.instructions = instructions

        for arg in self.arguments:
            if arg.type is None:
                raise InternalError("Not Implemented")

        self.type = FunctionType(name, [arg.type for arg in arguments], return_type)

    def verify(self, scope:Scope):
        super().verify(scope)
        self.type.verify(self)

        for instruction in self.instructions:
            instruction.verify(self)

    @ensure_verified
    def resolveType(self, scope:Scope):
        return self.type

    @ensure_verified
    def resolveCall(self, call:FunctionType, scope:Scope):
        if not self.resolveType(scope).checkCompatibility(call):
            raise TypeError("{} is not compatible with {}".format(call, self.resolveType(scope)))
        return self

    @property
    def children(self):
        return self._children

    def addChild(self, child:ScopeObject):
        super().addChild(child)
        self._children[child.name] = child

    def __repr__(self):
        return "{}({}):{}{}".format(self.__class__.__name__, self.name, self.type, self.instructions)

class ExternalFunction(Scope):
    external_name = None
    type = None

    def __init__(self, name:str, external_name:str, arguments:[Type], return_type:Type):
        super().__init__(name)
        self.type = FunctionType(external_name, arguments, return_type)

    def verify(self, scope:Scope):
        super().verify(scope)

    @ensure_verified
    def resolveType(self, scope:Scope):
        return self.type

    resolveCall = Function.resolveCall

    @property
    def children(self):
        return {}

    def addChild(self, child:ScopeObject):
        raise InternalError("Not Implemented")

    def __repr__(self):
        return "{}({}->{}):{}".format(self.__class__.__name__, self.name, self.external_name, self.type)

class FunctionType(Type):
    arguments = None
    return_type = None

    def __init__(self, name:str, arguments:[Type], return_type:Type = None):
        super().__init__(name)
        self.arguments = arguments
        self.return_type = return_type

    def verify(self, scope:Scope):
        super().verify(scope)

    @ensure_verified
    def resolveType(self, scope:Scope):
        raise InternalError("Not Implemented")

    @property
    def children(self):
        return {}

    def addChild(self, child):
        raise InternalError("Not Implemented")

    @ensure_verified
    def checkCompatibility(self, other:Type):
        if isinstance(other, FunctionType):
            for self_arg, other_arg in zip(self.arguments, other.arguments):
                if not self_arg.checkCompatibility(other_arg):
                    return False

            #TODO: Return type handling
            #if self.return_type is not None and other.return_type is not None:
            #    self.return_type.checkCompatibility(other.return_type)
            #elif self.return_type is None or other.return_type is None:
            #    raise TypeError("{} is not compatible with {}".format(self, other))
            return True
        return False

    def __repr__(self):
        return "{}({}):{}".format(self.__class__.__name__,
            ", ".join(repr(arg) for arg in self.arguments), self.return_type)

#
# Method
#

class Method(ScopeObject):
    overloads = None

    def __init__(self, name:str, overloads:[Function]):
        self.overloads = []
        super().__init__(name)

        for overload in overloads:
            self.addOverload(overload)

    def addOverload(self, overload:Function):
        overload.name = str(len(self.overloads))
        overload.parent = self
        self.overloads.append(overload)

    def verify(self, scope:Scope):
        super().verify(scope)

        for overload in self.overloads:
            overload.verify(scope)

    @ensure_verified
    def resolveAttribute(self, reference:str, scope:Scope):
        return None

    @ensure_verified
    def resolveType(self, scope:Scope):
        return MethodType(self.name, [fn.resolveType(scope) for fn in self.overloads])

    @ensure_verified
    def resolveCall(self, call:FunctionType, scope:Scope):
        matches = []

        for overload in self.overloads:
            type = overload.resolveType(scope)
            if type.checkCompatibility(call):
                matches.append(overload)

        if len(matches) < 1:
            raise TypeError("{} is not compatible with {}".format(call, self))
        elif len(matches) > 1:
            raise TypeError("Ambiguous overloads: {}".format(matches))
        return matches[0]

    def __repr__(self):
        return "{}({}){}".format(self.__class__.__name__, self.name, self.overloads)

class MethodType(Type):
    overloads = None

    def __init__(self, name:str, overloads:[FunctionType]):
        super().__init__(name)
        self.overloads = overloads

#
# Call
#

class Call(Object):
    called = None
    values = None

    def __init__(self, called:Object, values:[Object]):
        self.called = called
        self.values = values

    def verify(self, scope:Scope):
        super().verify(scope)

        self.called.verify(scope)
        arg_types = []
        for val in self.values:
            val.verify(scope)
            arg_types.append(val.resolveType(scope))

        call_type = FunctionType("", arg_types)
        self.called = self.called.resolveCall(call_type, scope)

    def resolveType(self, scope:Scope):
        return None

    def resolveAttribute(self, reference:str, scope:Scope):
        raise InternalError("Not Implemented")

    def __repr__(self):
        return "{}<{}>({})".format(self.__class__.__name__, self.called, self.values)

#
# Literal
#

class Literal(Object):
    data = None
    type = None

    def __init__(self, data, type:Type):
        self.data = data
        self.type = type

    def verify(self, scope:Scope):
        super().verify(scope)

        self.type.verify(scope)

    def resolveType(self, scope:Scope):
        return self.type

    def __repr__(self):
        return "{}<{}>".format(self.type, self.data)

#
# Reference
#

class Reference(Type):
    reference = None
    value = None

    def __init__(self, reference:str):
        self.reference = reference

    def verify(self, scope:Scope):
        Object.verify(self, scope)
        self.value = resolveReference(scope, self.reference)
        self.value.verify(scope)

    @ensure_verified
    def resolveType(self, scope:Scope):
        return self.value.resolveType(scope)

    @ensure_verified
    def resolveCall(self, call:FunctionType, scope:Scope):
        return self.value.resolveCall(call, scope)

    @property
    @ensure_verified
    def children(self):
        return self.value.children

    def addChild(self, child:ScopeObject):
        self.value.addChild(child)

    @ensure_verified
    def checkCompatibility(self, other:Type):
        return self.value.checkCompatibility(other)

    def __repr__(self):
        return "{}({})<{}>".format(self.__class__.__name__, self.reference, self.value)

#
# Comment
#

class Comment(Object):
    contents = None

    def __init__(self, contents):
        self.contents = contents

    def verify(self, scope:Scope):
        super().verify(scope)

    def resolveType(self, scope:Scope):
        return None

    def __repr__(self):
        return "{}<{}>".format(self.__class__.__name__, self.contents)

"""
#
# Methods
#

class MethodType(Type):
    overloads = None

    def __init__(self, overloads:[FunctionType]):
        self.overloads = overloads

    def verify(self, scope:Scope):
        pass

    def checkCompatibility(self, other:Type):
        if isinstance(other, MethodType):
            # sanity check
            if len(self.overloads) == len(other.overloads):
                # Check that there is a match to any overload in the other, for all overloads in this one
                return all(
                    any(self_over.checkCompatibility(other_over) for other_over in other.overloads)
                        for self_over in self.overloads)

    def collectAttributes(self, scope:Scope = None):
        return {fn.name: fn for fn in self.overloads}

    def resolveType(self, scope:Scope):
        raise InternalError("Not implemented")

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

    def resolveType(self, scope:Scope = None):
        return self.type

    def copy(self):
        return Variable(self.name, self.type)

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

"""
