from copy import copy
from contextlib import contextmanager, ExitStack

from ..errors import *

from .state import State
from .util import checkCompatibility
from .core import Context, Object, BoundObject, Type
from .links import Link, Attribute
from .dependent import DependentObject, DependentContext
from . import dependent

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
        if other.resolveValue() is self:
            return True

        if self.value is not None:
            return self.value.checkCompatibility(other, check_cache)

        if self._static_value_type is None:
            if self.value is None: raise TypeError()

            return self.value.checkCompatibility(other, check_cache)

        else:
            return self.static_value_type.checkCompatibility(other.resolveValue(), check_cache)

    @property
    def static_value_type(self):
        self._static_value_type = self._static_value_type or DependentObject(self.parent)
        if isinstance(self.type, DependentObject) and self._static_value_type.resolved_type is None:
            self._static_value_type.resolved_type = self.type
        return self._static_value_type

    @contextmanager
    def targetValue(self, value):
        old_value = self.value
        self.value = value

        stack = ExitStack()
        if self._static_value_type is not None:
            targets = [(self._static_value_type, value)]
            stack.enter_context(dependent.target(targets))

        with stack:
            yield

        self.value = old_value

    def __copy__(self):
        return Variable(self.name, copy(self.type), self.tokens)

    def __repr__(self):
        if self.value is not None:
            return "{}:= {}".format(self.name, self.value)
        return "{}:{}".format(self.name, self.type)
