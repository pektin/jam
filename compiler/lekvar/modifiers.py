from ..errors import *

from .core import Context, Object, BoundObject, Type
from .links import Link, ContextLink

#
# Constant
#

class Constant(Link):
    assigned = True

    def __init__(self, value:Object, tokens = None):
        BoundLink.__init__(self, value, tokens)

    @property
    def name(self):
        return self.value.name

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

class ConstantContext(ContextLink):
    def __getitem__(self, name:str):
        value = Constant(ContextLink.__getitem__(self, name))
        value.assigned = True
        return value

#
# Reference
#

class Reference(Link):
    def __init__(self, value:Object, tokens = None):
        BoundLink.__init__(self, value, tokens)

    def resolveType(self):
        return Reference(self.value.resolveType())
