import logging
from contextlib import contextmanager
from abc import abstractmethod as abstract, ABC, abstractproperty

from ..errors import *

# Python predefines
# Because most function arguments are declared with types before those types
# are defined, we just set them to null here. This makes the type declaration
# purely syntactic
Context = None
Object = None
BoundObject = None
Type = None
Variable = None
Module = None
Function = None
FunctionType = None
Method = None

#
# Infrastructure
#

def verify(module:Module, builtin:Module, logger = logging.getLogger()):
    # Set up the initial state before verifying
    State.builtins = builtin
    State.logger = logger.getChild("lekvar")

    State.logger.info(module)

    module.verify()

# Resolves a reference inside of a given scope.
def resolveReference(reference:str):
    found = []

    # Collect all objects with a name matching reference up the tree of scopes
    scope = State.scope
    while True:
        context = scope.local_context

        if context is not None and reference in context.children:
            found.append(context.children[reference])

        # Go to builtins once the top of the tree is reached, otherwise move up
        if scope is State.builtins:
            break
        else:
            scope = scope.bound_context.scope if (scope.bound_context is not None) else State.builtins

    # Only a single found object is valid
    if len(found) < 1:
        raise MissingReferenceError("No reference to {}".format(reference))
    elif len(found) > 1:
        raise AmbiguityError("Ambiguous reference to {}".format(reference))

    return found[0]

# More general copy function which handles None
def copy(obj):
    if obj is not None:
        return obj.copy()
    return None

# The global state for the verifier
class State:
    builtins = None
    logger = None
    scope = None

    @classmethod
    @contextmanager
    def scoped(cls, scope:BoundObject):
        previous = cls.scope
        cls.scope = scope
        yield
        cls.scope = previous

#
# Abstract Base Structures
#
# These structures form the basis of Lekvar. They provide the base functionality
# needed to implement higher level features.

class Context:
    scope = None
    children = None

    def __init__(self, scope:BoundObject, children:[BoundObject]):
        self.scope = scope

        self.children = {}
        for child in children:
            self.addChild(child)

    def copy(self):
        return list(map(copy, self.children.values()))

    def verify(self):
        for child in self.children.values():
            child.verify()

    def addChild(self, child):
        self.children[child.name] = child
        self.fakeChild(child)

    def fakeChild(self, child):
        child.bound_context = self

    def __add__(self, other:Context):
        for child in self.children.values():
            if child.name in other.children:
                raise AmbiguityError()

        return Context(None, self.children.values() + other.children.values())

    def __repr__(self):
        return "{}<{}>".format(self.__class__.__name__, ", ".join(map(str, self.children.values())))

class Object(ABC):
    # Should return a unverified deep copy of the object
    @abstract
    def copy(self):
        pass

    # The main verification function. Should raise a CompilerError on failure
    @abstract
    def verify(self):
        pass

    # Should return an instance of Type representing the type of the object
    # Returns None for instructions
    @abstract
    def resolveType(self) -> Context:
        pass

    # Should either return None or a context accessible from the global scope
    @property
    def global_context(self) -> Context:
        return None

    # Should either return None or a context accessibly from the local scope
    @property
    def local_context(self):
        return None

    # Should return a function object that matches a function signature
    def resolveCall(self, call:FunctionType) -> Function:
        raise TypeError("{} object is not callable".format(self))

    # Resolves an attribute
    # final
    def resolveAttribute(self, reference:str):
        instance_context = self.resolveType().instance_context

        if instance_context is not None:
            if self.global_context is not None:
                context = instance_context + self.global_context
            else:
                context = instance_context
        else:
            context = self.global_context

        if context is not None and reference in context.children:
            return context.children[reference]
        raise MissingReferenceError("{} does not have an attribute {}".format(self, reference))

    def __repr__(self):
        return "{}".format(self.__class__.__name__)

class BoundObject(Object):
    name = None
    bound_context = None

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.name)

class Type(BoundObject):
    @property
    def instance_context(self):
        None

    @abstract
    def checkCompatibility(self, other:Type) -> bool:
        pass

#
# Module
#
# A module represents a simple namespace container scope.

class Module(BoundObject):
    context = None
    main = None
    verified = False

    def __init__(self, name:str, children:[BoundObject], main:Function = None):
        super().__init__(name)

        self.context = Context(self, children)

        self.main = main
        self.context.fakeChild(self.main)

    def copy(self):
        return Module(self.name, copy(self.context))

    def verify(self):
        if self.verified: return
        verified = True

        with State.scoped(self):
            self.main.verify()
            self.context.verify()

    def resolveType(self):
        raise InternalError("Not Implemented")

    @property
    def local_context(self):
        return self.context

    @property
    def global_context(self):
        return self.context

    def __repr__(self):
        return "{}({})<{}>[{}]".format(self.__class__.__name__, self.name, self.main, self.context)

#
# Dependent Type
#
# A Dependent type acts as an interface for types. When a variable has a
# dependent type and is called, it's dependent type changes to reflect the call.
# This means that dependent types can be used to implement generics.

class DependentType(Type):
    compatibles = None
    target = None

    def __init__(self, compatibles:[Type] = None):
        if compatibles is None: compatibles = []
        self.compatibles = compatibles

    def copy(self):
        return DependentType(self.compatibles[:])

    def verify(self):
        pass

    def checkCompatibility(self, other:Type):
        # If dependent type is targeted, only check for the target type
        if self.target is not None:
            return self.target.checkCompatibility(other)

        # Check with all compatible types
        for type in self.compatibles:
            if not type.checkCompatibility(other):
                return False

        if other not in self.compatibles:
            self.compatibles.append(other)

        return True

    def resolveType(self):
        raise InternalError("Not Implemented")

    def __repr__(self):
        if self.target is None:
            return "{}<{}>".format(self.__class__.__name__, self.compatibles)
        else:
            return "{} as {}".format(self.__class__.__name__, self.target)

#
# Function
#
# Functions are a basic container for instructions.

class Function(BoundObject):
    local_context = None

    arguments = None
    instructions = None

    type = None
    dependent = False
    verified = False

    def __init__(self, name:str, arguments:[Variable], instructions:[Object], return_type:Type = None):
        super().__init__(name)

        self.local_context = Context(self, arguments)

        self.arguments = arguments
        self.instructions = instructions

        for arg in self.arguments:
            if arg.type is None:
                arg.type = DependentType()
                self.dependent = True

        self.type = FunctionType(name, [arg.type for arg in arguments], return_type)

    def copy(self):
        fn = Function(self.name, list(map(copy, self.arguments)), list(map(copy, self.instructions)), self.type.return_type)
        return fn

    def verify(self):
        if self.verified: return
        verified = True

        with State.scoped(self):
            self.type.verify()

            for instruction in self.instructions:
                instruction.verify()

            # Further, analytical verification
            self.verifySelf()

    def verifySelf(self):
        # Ensure non-void functions return
        if not any(isinstance(inst, Return) for inst in self.instructions) and self.type.return_type is not None:
            raise SemanticError("All code paths must return")

    def resolveType(self):
        return self.type

    def resolveCall(self, call:FunctionType):
        if not self.resolveType().checkCompatibility(call):
            raise TypeError("{} is not compatible with {}".format(call, self.resolveType()))

        if not self.dependent:
            return self

        fn = copy(self)
        for index, arg in enumerate(fn.arguments):
            if isinstance(arg.type, DependentType):
                fn.type.arguments[index] = arg.type.target = call.arguments[index]
        fn.verify()
        return fn

    def __repr__(self):
        return "{}<{}>({}):{}{}".format(self.__class__.__name__, self.dependent, self.name, self.type, self.instructions)

class ExternalFunction(BoundObject):
    external_name = None
    type = None

    dependent = False
    verified = False

    def __init__(self, name:str, external_name:str, arguments:[Type], return_type:Type):
        super().__init__(name)
        self.external_name = external_name
        self.type = FunctionType(external_name, arguments, return_type)

    def copy(self):
        raise InternalError("Not Implemented")

    def verify(self):
        if self.verified: return
        self.verified = True

        with State.scoped(self):
            self.type.verify()

    def resolveType(self):
        return self.type

    resolveCall = Function.resolveCall

    def children(self):
        return {}

    def addChild(self, child:BoundObject):
        raise InternalError("Not Implemented")

    def __repr__(self):
        return "{}({}->{}):{}".format(self.__class__.__name__, self.name, self.external_name, self.type)

class FunctionType(Type):
    arguments = None
    return_type = None

    verified = False

    def __init__(self, name:str, arguments:[Type], return_type:Type = None):
        super().__init__(name)
        self.arguments = arguments
        self.return_type = return_type

    def copy(self):
        return FunctionType(self.name, list(map(copy, self.arguments)), copy(self.return_type))

    def verify(self):
        if self.verified: return
        self.verified = True

        with State.scoped(self):
            for arg in self.arguments:
                arg.verify()
            if self.return_type is not None:
                self.return_type.verify()

    def resolveType(self):
        raise InternalError("Not Implemented")

    def checkCompatibility(self, other:Type):
        if isinstance(other, Reference):
            other = other.value

        if isinstance(other, FunctionType):
            if len(self.arguments) != len(other.arguments):
                return False

            for self_arg, other_arg in zip(self.arguments, other.arguments):
                if not self_arg.checkCompatibility(other_arg):
                    return other.checkCompatibility(self)

            return True
        return other.checkCompatibility(self)

    def __repr__(self):
        return "{}({}):{}".format(self.__class__.__name__,
            ", ".join(repr(arg) for arg in self.arguments), self.return_type)

#
# Method
#
# A method is a generic container for functions. It implements the functionality
# for function overloading.

class Method(BoundObject):
    overloads = None
    verified = False

    def __init__(self, name:str, overloads:[Function]):
        self.overloads = []
        super().__init__(name)

        for overload in overloads:
            self.addOverload(overload)

    def copy(self):
        return Method(self.name, list(map(copy, self.overloads)))

    def addOverload(self, overload:Function):
        overload.name = str(len(self.overloads))
        self.overloads.append(overload)

    def assimilate(self, other:Method):
        for overload in other.overloads:
            self.addOverload(overload)

    def verify(self):
        if self.verified: return
        self.verified = True

        with State.scoped(self):
            for overload in self.overloads:
                overload.verify()

    def resolveType(self):
        return MethodType(self.name, [fn.resolveType() for fn in self.overloads])

    def resolveCall(self, call:FunctionType):
        matches = []

        # Collect overloads which match the call type
        for overload in self.overloads:
            try:
                matches.append(overload.resolveCall(call))
            except TypeError:
                continue

        # Allow only one match
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
    instance_context = None

    verified = False

    def __init__(self, name:str, constructor:Method, attributes:[BoundObject]):
        super().__init__(name)

        self.instance_context = Context(self, attributes)

        # Convert constructor method of functions to method of constructors
        #TODO: Eliminate the need for this
        self.constructor = constructor
        for index, overload in enumerate(self.constructor.overloads):
            self.constructor.overloads[index] = Constructor(overload, self)

    def copy(self):
        return Class(self.name, copy(self.constructor),
            {name: copy(item) for name, item in self._attributes.items()})

    def verify(self):
        if self.verified: return
        verified = True

        with State.scoped(self):
            self.constructor.verify()
            self.instance_context.verify()

    def resolveCall(self, call:FunctionType):
        function = self.constructor.resolveCall(call)
        function.type.return_type = self
        return function

    def resolveType(self):
        raise InternalError("Not Implemented")

    def checkCompatibility(self, other:Type) -> bool:
        if isinstance(other, Reference):
            other = other.value

        return other is self

class Constructor(Function):
    def __init__(self, function:Function, constructing:Type):
        super().__init__(function.name, function.arguments, function.instructions, function.type.return_type)

        if function.type.return_type is not None:
            raise TypeError("Constructors must return nothing")
        function.type.return_type = constructing

    def verifySelf(self):
        for instruction in self.instructions:
            if isinstance(instruction, Return):
                raise SyntaxError("Returns within constructors are invalid")

#
# Variable
#
# A variable is a simple container for a value. The scope object may be used
# in conjunction with assignments and values for advanced functionality.

class Variable(BoundObject):
    type = None

    def __init__(self, name:str, type:Type = None):
        super().__init__(name)
        self.type = type

    def copy(self):
        return Variable(self.name, copy(self.type))

    def verify(self):
        if self.type is not None:
            self.type.verify()

    def resolveType(self):
        return self.type

    def __repr__(self):
        return "{}<{}>:{}".format(self.__class__.__name__, self.name, self.type)

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

    def copy(self):
        return Assignment(copy(self.variable), copy(self.value))

    def verify(self):
        self.scope = State.scope

        # Try resolving the reference. If resolution fails, add a new variable
        # to the scope.
        try:
            variable = resolveReference(self.variable.name)
        except MissingReferenceError:
            State.scope.local_context.addChild(self.variable)
        else:
            # Verify variable type
            if variable.type is None:
                variable.type = self.variable.type
            elif self.variable.type is not None:
                raise TypeError("Cannot override variable type")

            self.variable = variable

        self.value.verify()

        value_type = self.value.resolveType()
        # Infer or verify the variable type
        if self.variable.type is None:
            self.variable.type = value_type
        elif not self.variable.type.checkCompatibility(value_type):
            raise TypeError("Cannot assign {} of type {} to variable {} of type {}".format(self.value, value_type, self.variable, self.variable.type))

    def resolveType(self):
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
    function = None

    def __init__(self, called:Object, values:[Object]):
        self.called = called
        self.values = values
        self.function = None

    def copy(self):
        return Call(copy(self.called), list(map(copy, self.values)))

    def verify(self):
        super().verify()

        self.called.verify()

        # Verify arguments and create the function type of the call
        arg_types = []
        for val in self.values:
            val.verify()
            arg_types.append(val.resolveType())
        call_type = FunctionType("", arg_types)

        # Resolve the call
        self.function = self.called.resolveCall(call_type)

    def resolveType(self):
        return self.function.resolveType().return_type

    def __repr__(self):
        if self.function is None:
            return "{}<{}>({})".format(self.__class__.__name__, self.called, self.values)
        return "{}<{}>({})".format(self.__class__.__name__, self.function, self.values)

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

    def copy(self):
        return self

    def verify(self):
        super().verify()

        self.type.verify()

    def resolveType(self):
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

    verified = False

    def __init__(self, reference:str):
        self.reference = reference

    def copy(self):
        return Reference(self.reference)

    def verify(self):
        if self.verified: return
        self.verified = True

        # Resolve the reference using general reference resolution
        self.value = resolveReference(self.reference)
        self.value.verify()

    def resolveType(self):
        return self.value.resolveType()

    @property
    def local_context(self):
        return self.value.local_context

    @property
    def global_context(self):
        return self.value.global_context

    def resolveCall(self, call:FunctionType):
        return self.value.resolveCall(call)

    def checkCompatibility(self, other:Type):
        print(self)
        print(State.scope)
        return self.value.checkCompatibility(other)

    def __repr__(self):
        return "{}({})<{}>".format(self.__class__.__name__, self.reference, self.value)

class Attribute(Type):
    value = None
    reference = None
    attribute = None

    verified = False

    def __init__(self, value:Object, reference:str):
        self.value = value
        self.reference = reference

    def copy(self):
        return Attribute(copy(value), self.reference)

    def verify(self):
        if self.verified: return
        self.verified = True

        self.value.verify()
        # Resolve the attribute using the values attribute resolution
        self.attribute = self.value.resolveAttribute(self.reference)

        if self.attribute is None:
            raise MissingReferenceError("{} does not have an attribute {}".format(self.value, self.reference))

    def resolveType(self):
        return self.attribute.resolveType()

    def resolveCall(self, call:FunctionType):
        return self.attribute.resolveCall(call)

    def checkCompatibility(self, other:Type):
        return self.attribute.checkCompatibility(other)

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

    def copy(self):
        return Return(copy(self.value))

    def verify(self):
        self.value.verify()

        if not isinstance(State.scope, Function):
            raise SyntaxError("Cannot return outside of a method")
        self.function = State.scope

        # Infer function types
        if self.function.type.return_type is None:
            self.function.type.return_type = self.value.resolveType()
        else:
            self.function.type.return_type.checkCompatibility(self.value.resolveType())

    def resolveType(self):
        return None

#
# Comment
#
# A comment is a piece of metadata that is generally not compiled

class Comment(Object):
    contents = None

    def __init__(self, contents):
        self.contents = contents

    def copy(self):
        return Comment(self.contents)

    def verify(self):
        pass

    def resolveType(self):
        return None

    def __repr__(self):
        return "{}<{}>".format(self.__class__.__name__, self.contents)
