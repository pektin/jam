from ..errors import *

from .state import State
from .core import Context, Object, BoundObject, Type
from .function import Function

class Module(BoundObject):
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

        with State.scoped(self):
            for instruction in self.main:
                instruction.verify()
        self.context.verify()

    def resolveType(self):
        if self.type is not None:
            self.type = ModuleType([child.resolveType() for child in self.context])
        return self.type

    @property
    def local_context(self):
        return self.context

    def __repr__(self):
        return "module {}".format(self.name)

class ModuleType(Type):
    verified = False
    _context = None

    def __init__(self, context:Context, tokens = None):
        super().__init__(tokens)

        self._context = context

    def copy(self):
        return self

    def verify(self):
        if self.verified: return
        self.verified = True

        with State.scoped(self._context.scope):
            self._context.verify()

    def resolveType(self):
        raise InternalError("Not Implemented")

    @property
    def instance_context(self):
        return self._context

    def checkCompatibility(self, other:Type):
        raise InternalError("Not Implemented")

    def resolveCompatibility(self, other:Type):
        raise InternalError("Not Implemented")
