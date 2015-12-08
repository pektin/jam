from ..errors import *

from .core import Context, Object, BoundObject, Type
from .links import Link

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

