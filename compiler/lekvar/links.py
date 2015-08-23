from ..errors import *

from .core import Context, Object, BoundObject, Type
from .util import resolveReference, resolveAttribute
from .function import Function, FunctionType

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

    def resolveCall(self, call:FunctionType):
        return self.value.resolveCall(call)

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

    def copy(self):
        return Reference(self.reference, self.tokens)

    def verify(self):
        if self.verified: return
        self.verified = True

        # Resolve the reference using general reference resolution
        try:
            self.value = resolveReference(self.reference)
        except MissingReferenceError as e:
            e.addMessage("", self.tokens)
            raise e
        super().verify()

    def __repr__(self):
        return "{}".format(self.reference)

class Attribute(Link):
    # The object the value belongs to
    parent = None
    reference = None
    verified = False

    def __init__(self, parent:Object, reference:str, tokens = None):
        super().__init__(None, tokens)
        self.parent = parent
        self.reference = reference

    def copy(self):
        return Attribute(self.parent, self.reference, self.tokens)

    def verify(self):
        if self.verified: return
        self.verified = True

        self.parent.verify()
        # Resolve the attribute using the values attribute resolution
        try:
            self.value = resolveAttribute(self.parent, self.reference)
        except MissingReferenceError as e:
            e.addMessage("", self.tokens)
            raise e
        self.value.verify()

    def __repr__(self):
        return "{}.{}".format(self.parent, self.reference)
