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

    @property
    def local_context(self):
        return self.value.local_context

    def verify(self):
        if self.value is not None: return

        try:
            self.value = lekvar.util.resolveReference(self.path[0], self)
            self.path.pop(0)
        except MissingReferenceError as e:
            if hasattr(self.source, "name"):
                # Start from the path of the source
                path = os.path.dirname(self.source.name)
            else:
                # Otherwise use the cwd
                path = "."

            while len(self.path) > 0:
                path = os.path.join(path, self.path.pop(0))
                if os.path.isfile(path + ".jm"):
                    with open(path + ".jm", "r") as f:
                        self.value = parser.parseFile(f, lekvar.State.logger)
                        break

            if self.value is None:
                raise ImportError("Cannot find file to import", self.tokens)

        for name in self.path:
            self.value = lekvar.Attribute(self.value, name)

        super().verify()

lekvar.Import = Import
