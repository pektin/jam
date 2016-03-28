import os

from . import parser

from .. import errors
from .. import lekvar

class Import(lekvar.Link, lekvar.BoundObject):
    static = True
    path = None

    def __init__(self, path:[str], name:str = None, tokens = None):
        if name is None:
            name = path[-1]
        lekvar.Link.__init__(self, None, tokens)
        lekvar.BoundObject.__init__(self, name, tokens)
        self.tokens = tokens
        self.path = path

    @property
    def local_context(self):
        return self.value.local_context

    def verify(self):
        if self.value is not None: return

        index = 0 # in path

        found = lekvar.State.scope.resolveIdentifier(self.path[index])
        # Handle circular imports
        try:
            found.remove(self)
        except ValueError:
            pass

        if len(found) == 1:
            self.value = found[0]
            index += 1
        elif len(found) > 1:
            err = errors.AmbiguityError(message="Ambiguous reference to").add(content=self.path[index], object=self).addNote(message="Matches:")
            for match in found:
                err.addNote(object=match)
            raise err
        else:
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
                raise errors.ImportError(message="Cannot find file for").add(object=self)

        for name in self.path[index:]:
            self.value = lekvar.Attribute(self.value, name)

        lekvar.Link.verify(self)

    def parseSource(self, file):
        previous_sources = lekvar.State.sources

        if lekvar.State.sources is None:
            object = self
            while object.parent is not None:
                object = object.parent
            lekvar.State.sources = ((self.source, object),)

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
