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

    print(module)
    module.verify()

def resolveReference(scope:Object, reference:str):
    found = []

    def getattrs(scope):
        attrs = scope.collectAttributes(scope)
        if reference in attrs:
            found.append(attrs[reference])

    # If the object is a scope, resolve up the tree
    print(scope)
    getattrs(scope)
    if isinstance(scope, Scope):
        print(scope.parent)
        while scope.parent is not None:
            scope = scope.parent
            print(scope)
            getattrs(scope)
    print()

    # Check for reference in builtins
    getattrs(builtins)

    if len(found) < 1:
        raise MissingReferenceError("No reference to {}".format(reference))
    elif len(found) > 1:
        raise AmbiguetyError("Ambiguous reference to {}".format(reference))

    return found[0]

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

    def __init__(self, name):
        self.name = name

    @abstract
    def verify(self, scope:Scope = None):
        pass

    @abstract
    def resolveType(self, scope:Scope = None):
        pass

    def resolveAttribute(self, reference:str, scope:Scope = None):
        return super().resolveAttribute(reference, scope)

    def __repr__(self):
        return "{}({}):{}".format(self.__class__.__name__, self.name, self.resolveType())

class Scope(ScopeObject):
    def __init__(self, name, children:[ScopeObject]):
        super().__init__(name)

        for child in children:
            self.addChild(child)

    def verify(self, scope:Scope = None):
        for child in self.children.values():
            child.verify()

    def resolveAttribute(self, reference:str, scope:Scope = None):
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
        return "{}({})<{}>".format(self.__class__.__name__, self.name, self.children)

class Type(Scope):
    def __init__(self, name, attributes:[ScopeObject]):
        super().__init__(name, attributes)

    def resolveAttribute(self, reference:str, scope:Scope = None):
        super(ScopeObject).resolveAttribute(reference, scope)

    @abstract
    def checkCompatibility(self, other:Type):
        pass

    def __repr__(self):
        return "{}".format(self.__class__.__name__)

#
# Module
#

class Module(Scope):
    main = None
    _children = None

    def __init__(self, name:str, children:[ScopeObject], main:Function):
        print(children)
        self._children = {}
        super().__init__(name, children)
        self.main = main

    def verify(self, scope:Scope = None):
        super().verify()
        self.main.verify()

    def resolveType(self, scope:Scope = None):
        raise InternalError("Not Implemented")

    @property
    def children(self):
        return self._children

    def addChild(self, child:ScopeObject):
        super().addChild(child)
        self._children[child.name] = child

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

    def verify(self, scope:Scope = None):
        self.type.verify()

        for instruction in self.instructions:
            instruction.verify(self)

        super().verify()

    def resolveType(self, scope:Scope = None):
        return self.type

    def resolveCall(self, call:FunctionType, scope:Scope):
        self.resolveType(scope).checkCompatibility(call)
        return self

    @property
    def children(self):
        return self._children

    def addChild(self, child:ScopeObject):
        super().addChild(child)
        self._children[child.name] = child

class ExternalFunction(Scope):
    external_name = None
    type = None

    def __init__(self, name:str, external_name:str, arguments:[Type], return_type:Type):
        self.type = FunctionType(external_name, arguments, return_type)

    def verify(self, scope:Scope = None):
        pass

    def resolveType(self, scope:Scope = None):
        return self.type

    resolveCall = Function.resolveCall

    @property
    def children(self):
        raise InternalError("Not Implemented")

    def addChild(self, child:ScopeObject):
        raise InternalError("Not Implemented")

    def __repr__(self):
        return "{}({}->{}):{}".format(self.__class__.__name__, self.name, self.external_name, self.type)

class FunctionType(Type):
    arguments = None
    return_type = None

    def __init__(self, name:str, arguments:[Type], return_type:Type = None):
        self.arguments = arguments
        self.return_type = return_type

    def verify(self, scope:Scope = None):
        pass

    def resolveType(self, scope:Scope = None):
        raise InternalError("Not Implemented")

    @property
    def children(self):
        raise InternalError("Not Implemented")

    def addChild(self, child):
        raise InternalError("Not Implemented")

    def checkCompatibility(self, other:Type):
        if isinstance(other, FunctionType):
            for self_arg, other_arg in zip(self.arguments, other.arguments):
                self_arg.checkCompatibility(other.arguments)

            #if self.return_type is not None and other.return_type is not None:
            #    self.return_type.checkCompatibility(other.return_type)
            #elif self.return_type is None or other.return_type is None:
            #    raise TypeError("{} is not compatible with {}".format(self, other))
        else:
            raise TypeError("{} is not compatible with {}".format(self, other))

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
        self.called.verify(scope)
        arg_types = []
        for val in self.values:
            val.verify(scope)
            arg_types.append(val.resolveType(scope))

        call_type = FunctionType("", arg_types)
        self.called = called.resolveCall(call_type, scope)

    def resolveType(self, scope:Scope):
        return None

    def resolveAttribute(self, reference:str, scope:Scope):
        raise InternalError("Not Implemented")

#
# Method
#

class Method(Scope):
    pass

#
# Reference
#

class Reference(Object):
    reference = None
    value = None

    def __init__(self, reference:str):
        self.reference = reference

    def verify(self, scope:Scope):
        self.value = resolveReference(scope, self.reference)
        self.value.verify(scope)

    def resolveType(self, scope:Scope):
        return self.value.resolveType(scope)

    def resolveAttribute(self, reference:str, scope:Scope):
        return self.value.resolveAttribute(reference, scope)

    def resolveCall(self, call:FunctionType, scope:Scope):
        return self.value.resolveCall(call, scope)

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



"""
#
# Methods
#

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

    def resolveType(self, scope:Scope = None):
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
"""
