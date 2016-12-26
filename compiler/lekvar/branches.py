from contextlib import contextmanager

from ..errors import *

from .state import State
from .stats import SoftScopeStats
from .core import Context, Object, BoundObject, SoftScope, Type
from .function import Function
from .module import Module

#
# Loop
#

class Loop(SoftScope):
    function = None
    instructions = None
    local_context = None

    def __init__(self, instructions, tokens = None):
        SoftScope.__init__(self, tokens)

        self.instructions = instructions
        self.local_context = Context(self)

    def verify(self):
        self.function = State.scope

        self._stats = SoftScopeStats(self.function)

        with State.scoped(self, soft = True):
            for instruction in self.instructions:
                instruction.verify()

        # Update scope state
        State.soft_scope.stats.merge(self.stats)

    def resolveType(self):
        raise InternalError("Loop objects do not have a type")

#
# Break
#

class Break(Object):
    loop = None

    def __init__(self, tokens = None):
        Object.__init__(self, tokens)

    def verify(self):
        self.loop = State.getSoftScope(lambda a: isinstance(a, Loop))
        if self.loop is None:
            raise SyntaxError(message="Cannot").add(object=self).add(message="outside loop")

    def resolveType(self):
        raise InternalError("Break objects do not have a type")

#
# Branch
#

class Branch(SoftScope):
    function = None
    condition = None

    instructions = None
    local_context = None
    previous_branch = None
    next_branch = None

    def __init__(self, condition, instructions, next_branch = None, tokens = None):
        SoftScope.__init__(self, tokens)

        self.condition = condition

        self.instructions = instructions
        self.local_context = Context(self)
        self.next_branch = next_branch
        if next_branch is not None:
            next_branch.previous_branch = self

    def verify(self):
        self.function = State.scope

        self._stats = SoftScopeStats(self.function)

        if self.condition is not None:
            self.condition.verify()

        with State.scoped(self, soft = True):
            for instruction in self.instructions:
                instruction.verify()

        if self.next_branch is not None:
            self.next_branch.verify()
            self.stats.merge(self.next_branch.stats)

        if self.previous_branch is None:
            State.soft_scope.stats.update(self.stats)

    def resolveType(self):
        raise InternalError("Branch objects do not have a type")
