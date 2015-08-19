import os

from . import parser

from ..errors import *
from .. import lekvar

class Import(lekvar.Link, lekvar.BoundObject):
    static = True
    path = None

    def __init__(self, path:[str], name:str = None, tokens = None):
        if name is None:
            name = path[-1]
        super().__init__(None, name)
        self.tokens = tokens
        self.path = path
        print(self.value, self.tokens, self.name, self.path)

    @property
    def local_context(self):
        return self.value.local_context

    def copy(self):
        raise InternalError("Not Implemented")

    def verify(self):
        if self.value is not None: return

        try:
            self.value = lekvar.util.resolveReference(self.path[0])
            self.path.pop(0)
        except MissingReferenceError:
            raise InternalError("Not Implemented")

        for name in self.path:
            self.value = lekvar.Attribute(self.value, name)

        super().verify()

lekvar.Import = Import
