from ..errors import *

from .state import State
from .util import resolveReference, checkCompatibility, copy
from .core import Context, Object, BoundObject, Type

#
# Variable
#
# A variable is a simple container for a value. The scope object may be used
# in conjunction with assignments and values for advanced functionality.

class Variable(BoundObject):
    type = None

    def __init__(self, name:str, type:Type = None, tokens = None):
        super().__init__(name, tokens)
        self.type = type

    def copy(self):
        var = Variable(self.name, copy(self.type))
        var.static = self.static
        return var

    def verify(self):
        self.type.verify()

    def resolveType(self):
        return self.type

    @property
    def local_context(self):
        return None

    def __repr__(self):
        return "{}:{}".format(self.name, self.type)

#
# Assignment
#
# Assignment instructions allow for saving values inside of variables.

class Assignment(Object):
    variable = None
    value = None
    scope = None

    def __init__(self, variable:Variable, value:Object, tokens = None):
        super().__init__(tokens)
        self.variable = variable
        self.value = value

    def copy(self):
        return Assignment(copy(self.variable), copy(self.value))

    def verify(self):
        self.scope = State.scope

        # Try resolving the reference. If resolution fails, add a new variable
        # to the scope.
        try:
            variable = resolveReference(self.variable.name)
        except MissingReferenceError:
            State.scope.local_context.addChild(self.variable)
        else:
            # Verify variable type
            if variable.type is None:
                variable.type = self.variable.type
            elif self.variable.type is not None: #TODO: Maybe just verify compatibility?
                raise TypeError("Cannot override variable type", self.tokens)

            self.variable = variable

        self.value.verify()
        value_type = self.value.resolveType()

        # Infer the variable type if necessary
        if self.variable.type is None:
            self.variable.type = value_type

        self.variable.verify()

        # Verify the variable's type with the assigned values
        if not checkCompatibility(value_type, self.variable.type):
            raise TypeError("Cannot assign {} of type {} to variable {} of type {}".format(self.value, value_type, self.variable, self.variable.type),
                self.value.tokens + self.variable.tokens + self.tokens)

    def resolveType(self):
        raise InternalError("Assignments do not have types")

    def __repr__(self):
        return "{} = {}".format(self.variable, self.value)
