from ..errors import *

from .state import State
from .core import Context, Object, BoundObject, Type
from .util import resolveReference, resolveAttribute
from .variable import Variable

class Link(Type):
    value = None

    def __init__(self, value:Object, tokens = None):
        super().__init__(tokens)
        self.value = value

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

    def resolveCall(self, call):
        return self.value.resolveCall(call)

    def verifyAssignment(self, value):
        return self.value.verifyAssignment(value)

    def resolveValue(self):
        return self.value.resolveValue()

    def checkCompatibility(self, other:Type):
        return self.value.checkCompatibility(other)

    def resolveCompatibility(self, other:Type):
        return self.value.resolveCompatibility(other)

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

class Identifier(Link):
    identifier = None

    def __init__(self, identifier:str, tokens = None):
        super().__init__(None, tokens)
        self.identifier = identifier

    def verify(self):
        if self.value is not None: return

        try:
            self.value = resolveReference(self.identifier)
        except MissingReferenceError as e:
            e.add(content=self.identifier, object=self)
            raise e

        super().verify()

    def verifyAssignment(self, value):
        if self.value is not None: return

        # Infer variable existence
        try:
            self.value = resolveReference(self.identifier)
        except MissingReferenceError:
            self.value = Variable(self.identifier, value.resolveType())
            State.scope.local_context.addChild(self.value)

        self.value.verifyAssignment(value)

    def __repr__(self):
        return "{}".format(self.identifier)

class Attribute(Link):
    # The object the value belongs to
    parent = None
    name = None

    def __init__(self, parent:Object, name:str, tokens = None):
        super().__init__(None, tokens)
        self.parent = parent
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
        self.parent.verify()
        # Resolve the attribute using the values attribute resolution
        try:
            self.value = resolveAttribute(self.parent, self.name)
        except MissingReferenceError as e:
            e.add(content=self.name, object=self)
            raise e

    def __repr__(self):
        return "{}.{}".format(self.parent, self.name)
