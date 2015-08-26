from abc import abstractmethod as abstract, ABC, abstractproperty

from ..errors import *

from .state import State

# Python predefines
Object = None
BoundObject = None
Scope = None
Type = None
Function = None
FunctionType = None

# A context provides a useful wrapper around the mapping of child objects
# to their scope.
class Context:
    scope = None
    children = None

    def __init__(self, scope:BoundObject, children:[BoundObject]):
        self.scope = scope

        self.children = {}
        for child in children:
            self.addChild(child)

    # Verifies all child objects
    def verify(self):
        for child in self:
            child.verify()

    # Doubly link a child to the context
    def addChild(self, child):
        self.children[child.name] = child
        self.fakeChild(child)

    # Bind the child to the context, but not the context to the child
    # Useful for setting up "parenting" for internal objects
    def fakeChild(self, child):
        child.bound_context = self

    def __contains__(self, name:str):
        return name in self.children

    def __getitem__(self, name:str):
        return self.children[name]

    def __setitem__(self, name:str, value:BoundObject):
        self.children[name] = value

    # Iterate through the children (not their names)
    def __iter__(self):
        return iter(self.children.values())

    def __len__(self):
        return len(self.children)

    def __repr__(self):
        return "{}<{}>".format(self.__class__.__name__, ", ".join(map(str, self.children.values())))

# A generic object that represents a single value/instruction.
class Object(ABC):
    source = None
    tokens = None

    def __init__(self, tokens = None):
        self.source = State.source
        self.tokens = tokens

    # The main verification function. Should raise a CompilerError on failure
    @abstract
    def verify(self):
        pass

    # Should return an instance of Type representing the type of the object
    # Returns None for instructions
    @abstract
    def resolveType(self) -> Type:
        pass

    # Should return a Object inplace of the current one
    # only useful for objects that link to other objects
    def resolveValue(self) -> Object:
        return self

    # Resolves a call using this object's type.
    # May be overridden for more specific behaviour
    def resolveCall(self, call:FunctionType) -> Function:
        return self.resolveType().resolveInstanceCall(call)

    # Provides a context of attributes using this object's type.
    # May be overridden for more specific behaviour
    @property
    def context(self) -> Context:
        return self.resolveType().instance_context

    def __repr__(self):
        return "{}".format(self.__class__.__name__)

# A generic object that can be bound to a context. Any object that may have
# other objects bound to it through a context must also be a bound object.
class BoundObject(Object):
    name = None
    static = False
    dependent = False
    bound_context = None

    def __init__(self, name, tokens = None):
        super().__init__(tokens)
        self.name = name

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.name)

# A bound object that has a local context of all of its children
class Scope(BoundObject):
    # The local context provides the context accessible objects bound to a
    # context whose scope is this object.
    @abstractproperty
    def local_context(self):
        pass

# A type object that is used to describe certain behaviour of an object.
class Type(Object):
    # The attributes available on an instance
    @property
    def instance_context(self):
        return None

    # Resolves a call on an instance
    # Returns the function to call for that instance
    def resolveInstanceCall(self, call:FunctionType) -> Function:
        raise TypeError("Cannot call object of type {}".format(self), self.tokens)

    # Returns whether or not a given type is compatible with this type
    @abstract
    def checkCompatibility(self, other:Type) -> bool:
        pass
