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

def verify(module:Module, builtin:Module, logger:logging.Logger = None):
    State.builtins = builtin
    State.logger = logger or logging.getLogger()

    logger.info(module)
    module.verify(None)

class State:
    builtins = None
    logger = None

def resolveReference(scope:Scope, reference:str):
    found = []

    # If the object is a scope, resolve up the tree
    while scope is not None:
        attr = scope.resolveReference(scope, reference)

        if attr is not None:
            found.append(attr)

        if scope is State.builtins:
            break
        else:
            scope = scope.parent if (scope.parent is not None) else State.builtins

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
# These structures form the basis of Lekvar. They provide the base functionality
# needed to implement higher level features.

class Object(ABC):
    @abstract
    def verify(self, scope:Scope):
        pass

    @abstract
    def resolveType(self, scope:Scope):
        pass

    def resolveAttribute(self, scope:Scope, reference:str) -> Object:
        return self.resolveType(scope).resolveReference(scope, reference)

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

    @ensure_verified
    def resolveReference(self, scope:Scope, reference:str):
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
        return ScopeObject.resolveAttribute(self, scope, reference)

    @abstract
    @ensure_verified
    def checkCompatibility(self, scope:Scope, other:Type) -> bool:
        pass

#
# Module
#
# A module represents a simple namespace container scope.

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
# Dependent Type
#
# A Dependent type acts as an interface for types. When a variable has a
# dependent type and is called, it's dependent type changes to reflect the call.
# This means that dependent types can be used to implement generics.

class DependentType(Type):
    def __init__(self):
        self.compatibles = []

    def verify(self, scope:Scope):
        pass

    def addChild(self, child):
        raise InternalError("Not Implemented")

    @property
    def children(self):
        raise InternalError("Not Implemented")

    @ensure_verified
    def checkCompatibility(self, scope:Scope, other:Type):
        if isinstance(other, Reference):
            other = other.value

        for type in self.compatibles:
            if not type.checkCompatibility(scope, other):
                return False

        self.compatibles.append(other)
        return True

    @ensure_verified
    def resolveType(self, scope:Scope):
        raise InternalError("Not Implemented")

    def __repr__(self):
        return "{}<{}>".format(self.__class__.__name__, self.compatibles)

#
# Function
#
# Functions are a basic container for instructions.

class Function(Scope):
    _children = None
    arguments = None
    instructions = None
    type = None
    dependent = False

    def __init__(self, name:str, arguments:[Variable], instructions:[Object], return_type:Type = None):
        self._children = {}
        super().__init__(name, arguments)
        self.arguments = arguments
        self.instructions = instructions

        for arg in self.arguments:
            if arg.type is None:
                arg.type = DependentType()
                dependent = True

        self.type = FunctionType(name, [arg.type for arg in arguments], return_type)
        self.type.parent = self

    def verify(self, scope:Scope):
        if self.verified: return
        super().verify(scope)

        self.type.verify(self)

        for instruction in self.instructions:
            instruction.verify(self)

        self.verifySelf()

    def verifySelf(self):
        # Ensure non-void functions return
        if not any(isinstance(inst, Return) for inst in self.instructions) and self.type.return_type is not None:
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
                    return other.checkCompatibility(scope, self)

            return True
        return other.checkCompatibility(scope, self)

    def __repr__(self):
        return "{}({}):{}".format(self.__class__.__name__,
            ", ".join(repr(arg) for arg in self.arguments), self.return_type)

#
# Method
#
# A method is a generic container for functions. It implements the functionality
# for function overloading.

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
# Class
#
# A class provides a generic interface for creating user types.

class Class(Type):
    constructor = None
    _attributes = None

    def __init__(self, name:str, constructor:Method, attributes:{str: ScopeObject}):
        self._attributes = {}
        super().__init__(name, attributes)

        self.constructor = constructor
        self.constructor.parent = self
        for index, overload in enumerate(self.constructor.overloads):
            self.constructor.overloads[index] = Constructor(overload)
            self.constructor.overloads[index].parent = self.constructor

    def verify(self, scope:Scope):
        if self.verified: return
        super().verify(scope)
        self.constructor.verify(scope)

    @ensure_verified
    def resolveCall(self, scope:Scope, call:FunctionType):
        function = self.constructor.resolveCall(scope, call)
        function.type.return_type = self
        return function

    @ensure_verified
    def resolveType(self, scope:Scope):
        raise InternalError("Not Implemented")

    @property
    def children(self):
        return self._attributes

    def addChild(self, child:ScopeObject):
        super().addChild(child)
        self._attributes[child.name] = child

    @ensure_verified
    def checkCompatibility(self, scope:Scope, other:Type) -> bool:
        if isinstance(other, Reference):
            other = other.value

        return other is self

class Constructor(Function):
    def __init__(self, function:Function):
        super().__init__(function.name, function.arguments, function.instructions, function.type.return_type)

        if function.type.return_type is not None:
            raise TypeError("Constructors must return nothing")
        function.type.return_type = self.parent

    def verifySelf(self):
        for instruction in self.instructions:
            if isinstance(instruction, Return):
                raise SyntaxError("Returns within constructors are invalid")

#
# Variable
#
# A variable is a simple container for a value. The scope object may be used
# in conjunction with assignments and values for advanced functionality.

class Variable(ScopeObject):
    type = None

    def __init__(self, name:str, type:Type = None):
        super().__init__(name)
        self.type = type

    def copy(self):
        return Variable(self.name, self.type)

    def verify(self, scope:Scope):
        if self.type is not None:
            self.type.verify(scope)

    @ensure_verified
    def resolveType(self, scope:Scope):
        return self.type

#
# Assignment
#
# Assignment instructions allow for saving values inside of variables.

class Assignment(Object):
    variable = None
    value = None
    scope = None

    def __init__(self, variable:Variable, value:Object):
        self.variable = variable
        self.value = value

    def verify(self, scope:Scope):
        self.scope = scope

        try:
            variable = resolveReference(scope, self.variable.name)
        except MissingReferenceError:
            scope.addChild(self.variable)
        else:
            if variable.type is None:
                variable.type = self.variable.type
            elif self.variable.type is not None:
                raise TypeError("Cannot override variable type")

            self.variable = variable

        self.value.verify(scope)
        value_type = self.value.resolveType(scope)
        if self.variable.type is None:
            self.variable.type = value_type
        elif not self.variable.type.checkCompatibility(scope, value_type):
            raise TypeError("Cannot assign {} of type {} to variable {} of type {}".format(
                self.value, value_type, self.variable, self.variable.type))

    def resolveType(self, scope:Scope):
        return None

    def __repr__(self):
        return "{}<{} = {}>".format(self.__class__.__name__, self.variable, self.value)

#
# Call
#
# A call is a simple instruction to execute a given function with specific
# arguments.

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
# A literal is a direct piece of constant data in memory.

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
# A reference is a by-name link to a object in the current or parent scopes.
# References are used to prevent object duplication.

class Reference(Type):
    reference = None
    value = None

    def __init__(self, reference:str):
        self.reference = reference

    def verify(self, scope:Scope):
        if self.verified: return
        self.verified = True

        self.value = resolveReference(scope, self.reference)
        self.value.verify(scope)

    @ensure_verified
    def resolveType(self, scope:Scope):
        return self.value.resolveType(scope)

    @ensure_verified
    def resolveCall(self, scope:Scope, call:FunctionType):
        return self.value.resolveCall(scope, call)

    @property
    def children(self):
        return self.value.children

    def addChild(self, child:ScopeObject):
        self.value.addChild(child)

    @ensure_verified
    def checkCompatibility(self, scope:Scope, other:Type):
        return self.value.checkCompatibility(scope, other)

    def __repr__(self):
        return "{}({})<{}>".format(self.__class__.__name__, self.reference, self.value)

class Attribute(Type):
    value = None
    reference = None
    attribute = None

    def __init__(self, value:Object, reference:str):
        self.value = value
        self.reference = reference

    def verify(self, scope:Scope):
        if self.verified: return
        self.verified = True

        self.value.verify(scope)
        self.attribute = self.value.resolveAttribute(scope, self.reference)

        if self.attribute is None:
            raise MissingReferenceError("{} does not have an attribute {}".format(self.value, self.reference))

    @ensure_verified
    def resolveType(self, scope:Scope):
        return self.attribute.resolveType(scope)

    @ensure_verified
    def resolveCall(self, scope:Scope, call:FunctionType):
        return self.attribute.resolveCall(scope, call)

    @property
    def children(self):
        return self.attribute.children

    def addChild(self, child:ScopeObject):
        self.attribute.addChild(child)

    @ensure_verified
    def checkCompatibility(self, scope:Scope, other:Type):
        return self.attribute.checkCompatibility(scope, other)

    def __repr__(self):
        return "{}({}).{}<{}>".format(self.__class__.__name__, self.value, self.reference, self.attribute)

#
# Return
#
# Returns can only exist as instructions for functions. They cause the function
# to return with a specified value.

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
# A comment is a piece of metadata that is generally not compiled

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
