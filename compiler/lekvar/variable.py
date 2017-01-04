from copy import copy
from contextlib import contextmanager, ExitStack

from ..errors import *

from .state import State
from .stats import Stats
from .util import checkCompatibility
from .core import Context, Object, BoundObject, Type
from .links import Link, Attribute
from .forward import ForwardObject
from . import forward

#
# Variable
#
# A variable is a simple container for a value. The scope object may be used
# in conjunction with assignments and values for advanced functionality.

class Variable(BoundObject, Type):
    type = None
    value = None

    _static_value_type = None

    def __init__(self, name:str, type:Type = None, tokens = None):
        BoundObject.__init__(self, name, tokens)
        self.type = type

    def verify(self):
        self.type.verify()

        if not isinstance(self.type.resolveValue(), Type):
            raise TypeError(object=self.type).add(message="cannot be used as a type for").add(object=self)

        assert self.parent is not None
        self._stats = Stats(self.parent)
        if self.type.stats.forward or self._static_value_type is not None:
            self.stats.forward = True

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

    @property
    def instance_context(self):
        return self.static_value_type.instance_context

    def checkCompatibility(self, other:Type, check_cache = None):
        other = other.resolveValue()
        if other is self:
            return True

        if self.value is not None:
            return self.value.checkCompatibility(other, check_cache)

        return self.static_value_type.checkCompatibility(other, check_cache)

    def revCheckCompatibility(self, other:Type, check_cache = None):
        other = other.resolveValue()
        if other is self:
            return True

        if self.value is not None:
            return self.value.revCheckCompatibility(other, check_cache)

        return self.static_value_type.checkCompatibility(other, check_cache)

    @property
    def static_value_type(self):
        if self._static_value_type is None:
            self._static_value_type = ForwardObject(self.parent, self.name)
            # self._static_value_type.resolveType().compatible_types.add((self.type,))

        if isinstance(self.type, ForwardObject) and self._static_value_type.resolved_type is None:
            self._static_value_type.resolved_type = self.type
        return self._static_value_type

    @contextmanager
    def targetValue(self, value):
        old_value = self.value
        self.value = value

        stack = ExitStack()
        if self._static_value_type is not None:
            targets = [(self._static_value_type, value)]
            stack.enter_context(forward.target(targets))

        with stack:
            yield

        self.value = old_value

    def extractValue(self):
        if self._static_value_type is not None:
            return self.static_value_type
        return self

    def __copy__(self):
        return Variable(self.name, copy(self.type), self.tokens)

    def __repr__(self):
        if self.value is not None:
            return "{}:= {}".format(self.name, self.value)
        return "{}:{}".format(self.name, self.type)
