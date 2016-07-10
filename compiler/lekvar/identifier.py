from ..errors import *

from .state import State
from .links import BoundLink
from .variable import Variable
from .assignment import InferVariable

class Identifier(BoundLink):
    name = None

    def __init__(self, name:str, tokens = None):
        BoundLink.__init__(self, None, tokens)
        self.name = name

    def _resolveIdentifier(self):
        # Use sets to ignore duplicate entries
        #TODO: Fix duplicate entries
        found = set(State.scope.resolveIdentifier(self.name))
        found |= set(State.builtins.resolveIdentifier(self.name))

        if len(found) > 1:
            err = AmbiguityError(message="Ambiguous reference to").add(content=self.name, object=self).addNote(message="Matches:")
            for match in found:
                err.addNote(object=match)
            raise err

        return found

    def verify(self):
        if self.value is not None: return

        found = self._resolveIdentifier()

        if len(found) < 1:
            raise MissingReferenceError(message="Missing reference to").add(content=self.name, object=self)

        self.value = found.pop()

        BoundLink.verify(self)

    def verifyAssignment(self, value):
        if self.value is not None:
            return BoundLink.verifyAssignment(self, value)

        found = self._resolveIdentifier()

        if len(found) == 1:
            self.value = found.pop()
            return BoundLink.verifyAssignment(self, value)
        # Infer variable existence
        else:
            # Inject a new variable into the enclosing hard scope
            self.value = Variable(self.name, value.resolveType())
            # Make variable have the same tokens. Hack for nicer error messages
            self.value.tokens = self.tokens
            self.value.source = self.source

            BoundLink.verifyAssignment(self, value)
            raise InferVariable()

    def __repr__(self):
        return "{}".format(self.name)
