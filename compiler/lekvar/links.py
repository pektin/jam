from ..errors import *

from .state import State
from .core import Context, Object, BoundObject, Type
from .util import resolveReference, resolveAttribute
from .variable import Variable

class Link(Type):
    value = None

    def __init__(self, value:Object = None, tokens = None):
        super().__init__(tokens)
        self.value = value

    @property
    def dependent(self):
        return self.value.dependent

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

class Reference(Link):
    reference = None
    verified = False

    def __init__(self, reference:str, tokens = None):
        super().__init__(None, tokens)
        self.reference = reference

    def verify(self):
        if self.value is not None: return

        try:
            self.value = resolveReference(self.reference)
        except MissingReferenceError as e:
            e.add(content=self.reference, object=self)
            raise e

        super().verify()

    def verifyAssignment(self, value):
        if self.value is not None: return

        # Infer variable existence
        try:
            self.value = resolveReference(self.reference)
        except MissingReferenceError:
            self.value = Variable(self.reference, value.resolveType())
            State.scope.local_context.addChild(self.value)

        self.value.verifyAssignment(value)

    def __repr__(self):
        return "{}".format(self.reference)

class Attribute(Link):
    # The object the value belongs to
    parent = None
    reference = None

    def __init__(self, parent:Object, reference:str, tokens = None):
        super().__init__(None, tokens)
        self.parent = parent
        self.reference = reference

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
            self.value = resolveAttribute(self.parent, self.reference)
        except MissingReferenceError as e:
            e.add(content=self.reference, object=self)
            raise e

    def __repr__(self):
        return "{}.{}".format(self.parent, self.reference)
