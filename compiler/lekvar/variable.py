from copy import copy

from ..errors import *

from .state import State
from .util import checkCompatibility
from .core import Context, Object, BoundObject, Type
from .links import Attribute

#
# Variable
#
# A variable is a simple container for a value. The scope object may be used
# in conjunction with assignments and values for advanced functionality.

class Variable(BoundObject):
    type = None

    def __init__(self, name:str, type:Type = None, tokens = None):
        BoundObject.__init__(self, name, tokens)
        self.type = type

    def verify(self):
        self.type.verify()

        if not isinstance(self.type.resolveValue(), Type):
            raise TypeError(object=self.type).add("cannot be used as a type for").add(object=self)

    def resolveType(self):
        return self.type

    def resolveCall(self, call):
        function = BoundObject.resolveCall(self, call)
        return Attribute(self, value = function)

    def verifyAssignment(self, value:Object):
        if value is None:
            return

        if self.type is None:
            self.type = value.resolveType()

        self.verify()

        if not checkCompatibility(value.resolveType(), self.type):
            raise (TypeError(message="Cannot assign").add(object=value)
                        .add(message="of type").add(object=value.resolveType())
                        .add(message="to").add(object=self))

    def __copy__(self):
        return Variable(self.name, copy(self.type), self.tokens)

    def __repr__(self):
        return "{}:{}".format(self.name, self.type)
