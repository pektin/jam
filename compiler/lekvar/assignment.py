from ..errors import *

from .state import State
from .core import Context, Object, BoundObject, Type

#
# Assignment
#
# Assignment instructions allow for saving values inside of variables.

class Assignment(Object):
    assigned = None
    value = None
    scope = None

    def __init__(self, assigned:Object, value:Object, tokens = None):
        Object.__init__(self, tokens)
        self.assigned = assigned
        self.value = value

    def verify(self):
        self.scope = State.scope

        self.value.verify()

        try:
            self.assigned.verifyAssignment(self.value)
        except TypeError as e:
            e.add(message="", object=self)
            raise
        except InferVariable as e:
            State.scope.local_context.addChild(self.assigned)
            e.variable.verifyAssignment(self.value)

    def resolveType(self):
        raise InternalError("Assignments do not have types")

    def __repr__(self):
        return "{} = {}".format(self.assigned, self.value)

# Evil exception hack for inferring variables
class InferVariable(Exception):
    def __init__(self, variable):
        self.variable = variable
