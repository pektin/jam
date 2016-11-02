from ..errors import *

from .state import State
from .core import Context, Object, BoundObject, Scope, Type
from .function import Function

class Module(Type, Scope):
    verified = False
    context = None
    static = True
    static_scope = True
    type = None

    def __init__(self, name:str, children:[BoundObject], main:[Object] = [], tokens = None):
        Scope.__init__(self, name, tokens)

        self.main = main
        self.context = Context(self, children)

    def verify(self):
        if self.verified: return
        self.verified = True

        with State.scoped(self, analys = True):
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
