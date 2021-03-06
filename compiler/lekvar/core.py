from abc import abstractmethod as abstract, ABC, abstractproperty

from ..errors import *

from .state import State
from .stats import Stats, SoftScopeStats, ScopeStats

# Python predefines
Object = None
BoundObject = None
SoftScope = None
Scope = None
Type = None
Function = None
FunctionType = None

# A context provides a useful wrapper around the mapping of child objects
# to their scope.
class Context:
    scope = None
    children = None

    def __init__(self, scope:SoftScope, children:[BoundObject] = []):
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
        assert hasattr(child, "bound_context")
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
    _stats = None

    def __init__(self, tokens = None):
        self.source = State.source
        self.tokens = tokens

    # The main verification function. Should raise a CompilerError on failure
    @abstract
    def verify(self):
        pass

    # Verify the object as the lhs of an assignment.
    # Should compliment verify if assignment is allowed.P
    def verifyAssignment(self, value:Object):
        raise TypeError(object=self).add(message="is not assignable")

    # Should return an instance of Type representing the type of the object
    # Returns None for instructions
    @abstract
    def resolveType(self) -> Type:
        pass

    # Resolve transparent links to other objects.
    # Only links which act solely as proxies should resolve to their linked value.
    def resolveValue(self) -> Object:
        return self

    # Deep extract a linked value.
    # Should bypass any features proxies on top of a linked value.
    def extractValue(self) -> Object:
        return self

    # Resolves a call operation using this object's type.
    # May be overridden for more specific behaviour
    def resolveCall(self, call:FunctionType) -> Function:
        return self.resolveType().resolveInstanceCall(call)

    # Provides a context of attributes using this object's type.
    # May be overridden for more specific behaviour
    @property
    def context(self) -> Context:
        return self.resolveType().instance_context

    @property
    def stats(self):
        assert self._stats is not None
        return self._stats

    # Create a copy, assuming the copy exists in the same context
    def __copy__(self):
        raise InternalError("Not Implemented");

    def __repr__(self):
        return "{}".format(self.__class__.__name__)

# A generic object that can be bound to a context. Any object that may have
# other objects bound to it through a context must also be a bound object.
class BoundObject(Object):
    name = None
    bound_context = None

    def __init__(self, name, tokens = None):
        Object.__init__(self, tokens)
        self.name = name

    @property
    def parent(self):
        if self.bound_context is None:
            return None
        return self.bound_context.scope

    def resolveIdentifier(self, name:str, exclude = []):
        if self.parent is not None:
            return self.parent.resolveIdentifier(name, exclude)
        return []

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.name)

# A generic object that has a local context of children
class SoftScope(Object):
    # The local context provides the context accessible objects bound to a
    # context whose scope is this object.
    @abstractproperty
    def local_context(self):
        pass

    def resolveIdentifier(self, name:str, exclude = []):
        if self.local_context is not None and name in self.local_context:
            if self.local_context[name] not in exclude:
                return [self.local_context[name]]
        return []

# A bound object that has a local context of all of its children
class Scope(SoftScope, BoundObject):
    def resolveIdentifier(self, name:str, exclude = []):
        return BoundObject.resolveIdentifier(self, name, exclude) + SoftScope.resolveIdentifier(self, name, exclude)

# A type object that is used to describe certain behaviour of an object.
class Type(Object):
    def resolveType(self):
        raise InternalError("Not Implemented")

    # The attributes available on an instance
    @property
    def instance_context(self):
        return None

    # Resolves a call on an instance
    # Returns the function to call for that instance
    def resolveInstanceCall(self, call:FunctionType) -> Function:
        raise TypeError(message="Cannot call object of type").add(object=self)

    # Returns whether or not a given type is compatible with this type
    @abstract
    def checkCompatibility(self, other:Type, check_cache:{Type: {Type} } = None) -> bool:
        pass

    def revCheckCompatibility(self, other:Type, check_cache:{Type: {Type} } = None) -> bool:
        return self.checkCompatibility(other, check_cache)
