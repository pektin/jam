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
        index = 0

        try:
            self.value = lekvar.util.resolveReference(self.path[index], self)
            index += 1
        except MissingReferenceError as e:
            if hasattr(self.source, "name"):
                # Start from the path of the source
                path = os.path.dirname(self.source.name)
            else:
                # Otherwise use the cwd
                path = "."

            while index < len(self.path):
                path = os.path.join(path, self.path[index])
                index += 1
                if os.path.isfile(path + ".jm"):
                    with open(path + ".jm", "r") as f:
                        self.parseSource(f)
                        break

            if self.value is None:
                raise ImportError("Cannot find file to import", self.tokens)

        for name in self.path[index:]:
            self.value = lekvar.Attribute(self.value, name)

        super().verify()

    def parseSource(self, file):
        previous_sources = lekvar.State.sources

        if lekvar.State.sources is None:
            parent = self
            while parent.bound_context is not None:
                parent = parent.bound_context.scope
            lekvar.State.sources = ((self.source, parent),)

        # Check if we have already parsed the file
        if hasattr(file, "fileno"):
            for src, module in lekvar.State.sources:
                if hasattr(src, "fileno") and os.path.sameopenfile(file.fileno(), src.fileno()):
                    self.value = module
                    break

        if self.value is None:
            self.value = parser.parseFile(file, lekvar.State.logger)
            lekvar.State.sources = tuple(list(lekvar.State.sources) + [(file, module)])
            # Must verify the module here, or imports in said module may use a closed file (self.source)
            self.value.verify()

        lekvar.State.sources = previous_sources

lekvar.Import = Import
