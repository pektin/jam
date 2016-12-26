from ..errors import *

from .state import State
from .stats import ScopeStats
from .core import Context, Object, BoundObject, Scope, Type
from .function import Function

class Module(Type, Scope):
    verified = False
    context = None
    type = None

    def __init__(self, name:str, children:[BoundObject], main:[Object] = [], tokens = None):
        Scope.__init__(self, name, tokens)

        self.main = main
        self.context = Context(self, children)

    def verify(self):
        if self.verified: return
        self.verified = True

        self._stats = ScopeStats(self.parent)
        if self.parent is None:
            self.stats.static = True

        with State.scoped(self):
            for instruction in self.main:
                instruction.verify()

            self.context.verify()

    def resolveType(self):
        return self

    @property
    def local_context(self):
        return self.context

    def checkCompatibility(self, other:Type, check_cache = None):
        raise InternalError("Not Implemented")

    def __repr__(self):
        return "module {}".format(self.name)
