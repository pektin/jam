from ..errors import *

from .state import State
from .core import Context, Object, BoundObject, Type
from .function import Function

class Module(Type):
    verified = False
    context = None
    static = True
    type = None

    def __init__(self, name:str, children:[BoundObject], main:[Object] = [], tokens = None):
        super().__init__(name, tokens)

        self.main = main
        self.context = Context(self, children)

        # All inherit static-ness
        for child in self.context:
            child.static = True

    # Singletons can't be copied
    def copy(self):
        return self

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

    def checkCompatibility(self, other:Type):
        raise InternalError("Not Implemented")

    def __repr__(self):
        return "module {}".format(self.name)
