from ..errors import *

from .core import Context, Object, BoundObject, Type
from .links import BoundLink, ContextLink

#
# Constant
#

class Constant(BoundLink):
    assigned = False

    def __init__(self, value:Object, tokens = None):
        BoundLink.__init__(self, value, tokens)

    def verifyAssignment(self, value):
        if self.assigned:
            raise TypeError(message="Cannot assign to constant").add(object=self)
        self.assigned = True

        self.value.verifyAssignment(value)

    def resolveType(self):
        return Constant(self.value.resolveType())

    @property
    def context(self):
        return ConstantContext(self.value.context)

    @property
    def local_context(self):
        return ConstantContext(self.value.local_context)

    @property
    def instance_context(self):
        return ConstantContext(self.value.instance_context)

    def __repr__(self):
        return "const({})".format(self.value)

class ConstantContext(ContextLink):
    def __getitem__(self, name:str):
        value = Constant(ContextLink.__getitem__(self, name))
        value.assigned = True
        return value

#
# Reference
#

class Reference(BoundLink):
    def __init__(self, value:Object, tokens = None):
        BoundLink.__init__(self, value, tokens)

    def resolveValue(self):
        return self

    def resolveType(self):
        return Reference(self.value.resolveType())

    def checkCompatibility(self, other):
        if isinstance(other, Reference):
            return self.value.checkCompatibility(other.value)

        return self.value.checkCompatibility(other)

    def __repr__(self):
        return "ref {}".format(self.value)
