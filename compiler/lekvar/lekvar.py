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
Method = None
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

    logger.info(module)
    module.verify(None)

def resolveReference(scope:Object, reference:str):
    found = []

    # If the object is a scope, resolve up the tree

    while scope is not None:
        attr = scope.resolveAttribute(scope, reference)
        if attr is not None:
            found.append(attr)

        if scope is builtins:
            break
        else:
            scope = scope.parent if scope.parent is not None else builtins

    if len(found) < 1:
        raise MissingReferenceError("No reference to {}".format(reference))
    elif len(found) > 1:
        raise AmbiguetyError("Ambiguous reference to {}".format(reference))

    return found[0]

def ensure_verified(fn):
    def func(self, *args):
        if not self.verified:
            self.verify(args[0])
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

    def resolveAttribute(self, scope:Scope, reference:str) -> Object:
        attributes = self.resolveType(scope).attributes
        if reference in attributes:
            return attributes[reference]
        return None

    def resolveCall(self, scope:Scope, call:FunctionType) -> Function:
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
    def resolveAttribute(self, scope:Scope, reference:str):
        return super().resolveAttribute(scope, reference)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.name)

class Scope(ScopeObject):
    def __init__(self, name, children:[ScopeObject] = []):
        super().__init__(name)

        for child in children:
            self.addChild(child)

    def verify(self, scope:Scope):
        if self.verified: return
        super().verify(scope)

        for child in self.children.values():
            child.verify(self)

    @ensure_verified
    def resolveAttribute(self, scope:Scope, reference:str):
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
    def resolveAttribute(self, scope:Scope, reference:str):
        ScopeObject.resolveAttribute(self, scope, reference)

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
        self.main.parent = self

    def verify(self, scope:Scope):
        if self.verified: return
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

    def __init__(self, name:str, arguments:[Variable], instructions:[Object], return_type:Type = None):
        self._children = {}
        super().__init__(name, arguments)
        self.arguments = arguments
        self.instructions = instructions

        for arg in self.arguments:
            if arg.type is None:
                raise InternalError("Not Implemented")

        self.type = FunctionType(name, [arg.type for arg in arguments], return_type)
        self.type.parent = self

    def verify(self, scope:Scope):
        if self.verified: return
        super().verify(scope)

        self.type.verify(self)

        returned = False

        for instruction in self.instructions:
            if isinstance(instruction, Return):
                returned = True
            instruction.verify(self)

        if not returned and self.type.return_type is not None:
            raise SemanticError("All code paths must return")

    @ensure_verified
    def resolveType(self, scope:Scope):
        return self.type

    @ensure_verified
    def resolveCall(self, scope:Scope, call:FunctionType):
        if not self.resolveType(scope).checkCompatibility(self, call):
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
        self.external_name = external_name
        self.type = FunctionType(external_name, arguments, return_type)
        self.type.parent = self

    def verify(self, scope:Scope):
        if self.verified: return
        super().verify(scope)

        self.type.verify(self)

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
        if self.verified: return
        super().verify(scope)

        for arg in self.arguments:
            arg.verify(self)
        if self.return_type is not None:
            self.return_type.verify(self)

    @ensure_verified
    def resolveType(self, scope:Scope):
        raise InternalError("Not Implemented")

    @ensure_verified
    def resolveAttribute(self, scope:Scope, reference:str):
        return None

    @property
    def children(self):
        return {}

    def addChild(self, child):
        raise InternalError("Not Implemented")

    @ensure_verified
    def checkCompatibility(self, scope:Scope, other:Type):
        if isinstance(other, Reference):
            other = other.value

        if isinstance(other, FunctionType):
            if len(self.arguments) != len(other.arguments):
                return False

            for self_arg, other_arg in zip(self.arguments, other.arguments):
                if not self_arg.checkCompatibility(scope, other_arg):
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

class Method(Scope):
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

    def assimilate(self, other:Method):
        for overload in other.overloads:
            self.addOverload(overload)

    @property
    def children(self):
        return {}

    def addChild(self, child:ScopeObject):
        raise InternalError("Not Implemented")

    def verify(self, scope:Scope):
        if self.verified: return
        super().verify(self)

        for overload in self.overloads:
            overload.verify(self)

    @ensure_verified
    def resolveAttribute(self, scope:Scope, reference:str):
        return None

    @ensure_verified
    def resolveType(self, scope:Scope):
        return MethodType(self.name, [fn.resolveType(scope) for fn in self.overloads])

    @ensure_verified
    def resolveCall(self, scope:Scope, call:FunctionType):
        matches = []

        for overload in self.overloads:
            type = overload.resolveType(scope)
            if type.checkCompatibility(self, call):
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
# Variable
#

class Variable(ScopeObject):
    type = None

    def __init__(self, name:str, type:Type = None):
        super().__init__(name)
        self.type = type

    def copy(self):
        return Variable(self.name, self.type)

    def verify(self, scope:Scope):
        pass

    @ensure_verified
    def resolveType(self, scope:Scope):
        return self.type

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
        self.called = self.called.resolveCall(scope, call_type)

    def resolveType(self, scope:Scope):
        return self.called.resolveType(scope).return_type

    def resolveAttribute(self, scope:Scope, reference:str):
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
        if self.verified: return
        self.verified = True
        Object.verify(self, scope)

        self.value = resolveReference(scope, self.reference)
        self.value.verify(scope)

    @ensure_verified
    def resolveType(self, scope:Scope):
        return self.value.resolveType(scope)

    @ensure_verified
    def resolveCall(self, scope:Scope, call:FunctionType):
        return self.value.resolveCall(scope, call)

    @property
    @ensure_verified
    def children(self):
        return self.value.children

    def addChild(self, child:ScopeObject):
        self.value.addChild(child)

    @ensure_verified
    def checkCompatibility(self, scope:Scope, other:Type):
        return self.value.checkCompatibility(scope, other)

    def __repr__(self):
        return "{}({})<{}>".format(self.__class__.__name__, self.reference, self.value)

#
# Return
#

class Return(Object):
    value = None
    function = None

    def __init__(self, value:Object = None):
        self.value = value

    def verify(self, scope:Scope):
        self.value.verify(scope)

        if not isinstance(scope, Function):
            raise SyntaxError("Cannot return outside of a method")
        self.function = scope

        # Infer function types
        if self.function.type.return_type is None:
            self.function.type.return_type = self.value.resolveType(scope)
        else:
            self.function.type.return_type.resolveCompatibility(self.value.resolveType(scope))

    def resolveType(self, scope:Scope):
        return None

#
# Comment
#

class Comment(Object):
    contents = None

    def __init__(self, contents):
        self.contents = contents

    def verify(self, scope:Scope):
        pass

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
"""
