from ..errors import *

from .core import BoundObject, Type
from .stats import ScopeStats

class VoidType(Type, BoundObject):
    def __init__(self, name:str = ""):
        BoundObject.__init__(self, name)

    def verify(self):
        self._stats = ScopeStats(self.parent)
        self.stats.static = True
        self.stats.forward = False

    def resolveType(self):
        raise InternalError("Void is typeless")

    @property
    def local_context(self):
        raise InternalError("Void does not have a local context")

    def checkCompatibility(self, other:Type, check_cache = None):
        # Void is compatible with all
        return True

    def __repr__(self):
        return "{}<{}>".format(self.__class__.__name__, self.name)
