from ..errors import *

from .core import Context, Object, BoundObject, Type
from .links import Link, ContextLink

#
# Constant
#

class Constant(Link):
    assigned = False

    def __init__(self, value:Object, assigned = False):
        self.value = value
        self.assigned = assigned

    @property
    def name(self):
        return self.value.name

    def verifyAssignment(self, value):
        if self.assigned:
            raise TypeError(message="Cannot assign to constant").add(object=self)
        self.assigned = True

        self.value.verifyAssignment(value)

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
        return Constant(super().__getitem__(name))

#
# Reference
#

class Reference(Link):
    def __init__(self, value:Object, tokens = None):
        super().__init__(value, tokens)

    def resolveType(self):
        return Reference(self.value.resolveType())
