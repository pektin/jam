from ..errors import *

from .core import Context, Object, BoundObject, Type
from .util import resolveAttribute

class Link(Type):
    value = None

    def __init__(self, value:Object, tokens = None):
        Type.__init__(self, tokens)
        self.value = value

    def __eq__(self, other):
        return self.value == other

    def __hash__(self):
        return hash(self.value)

    # Dispatch all functions to the linked value

    def verify(self):
        self.value.verify()

    def resolveType(self):
        return self.value.resolveType()

    @property
    def context(self):
        return self.value.context

    @property
    def instance_context(self):
        return self.value.instance_context

    @property
    def static(self):
        return self.value.static

    @property
    def static_scope(self):
        return self.value.static_scope

    def resolveCall(self, call):
        return self.value.resolveCall(call)

    def verifyAssignment(self, value):
        self.value.verifyAssignment(value)

    def resolveValue(self):
        return self.value.resolveValue()

    def extractValue(self):
        return self.value.extractValue()

    def checkCompatibility(self, other:Type, check_cache = None):
        return self.value.checkCompatibility(other, check_cache)

    def revCheckCompatibility(self, other:Type, check_cache = None):
        return self.value.revCheckCompatibility(other, check_cache)

    def resolveCompatibility(self, other:Type):
        return self.value.resolveCompatibility(other)

    def __copy__(self):
        return Link(self)

    def __repr__(self):
        return repr(self.value)

class BoundLink(Link, BoundObject):
    @property
    def name(self):
        return self.value.name

    @property
    def bound_context(self):
        return self.value.bound_context
    @bound_context.setter
    def bound_context(self, value):
        self.value.bound_context = value

    @property
    def is_bound(self):
        return isinstance(self.value, BoundObject)

class ContextLink:
    value = None

    def __init__(self, value:Context):
        self.value = value

    # Verifies all child objects
    def verify(self):
        self.value.verify()

    def __contains__(self, name:str):
        return name in self.value

    def __getitem__(self, name:str):
        return self.value[name]

    def __setitem__(self, name:str, value:BoundObject):
        self.value[name] = value

    # Iterate through the children (not their names)
    def __iter__(self):
        return iter(self.value)

    def __len__(self):
        return len(self.value)

    def __repr__(self):
        return repr(self.value)

class Attribute(Link):
    # The object the value belongs to
    object = None
    name = None

    def __init__(self, object:Object, name:str = "", tokens = None, value = None):
        Link.__init__(self, value, tokens)
        self.object = object
        self.name = name

    def verify(self):
        if self.value is not None: return

        self._verify()
        self.value.verify()

    def verifyAssignment(self, value):
        if self.value is not None: return

        self._verify()
        self.value.verifyAssignment(value)

    def _verify(self):
        self.object.verify()
        # Resolve the attribute using the values attribute resolution
        try:
            self.value = resolveAttribute(self.object, self.name)
        except MissingReferenceError as e:
            e.add(content=self.name, object=self)
            raise e

    def __repr__(self):
        if self.value is not None:
            return "{}.{}({})".format(self.object, self.name, self.value)
        return "{}.{}".format(self.object, self.name)
