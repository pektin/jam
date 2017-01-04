from contextlib import contextmanager, ExitStack

from .. import errors
from .. import lekvar
from .. import interpreter

class Pragma(lekvar.BoundLink):
    has_run = False

    def verify(self):
        if self.has_run: return
        self.has_run = True

        self.value.verify()
        self._run()

    def resolveValue(self):
        if self.value is None:
            return None
        return self.value.resolveValue()

    def _run(self):
        interpreter.State.stdout = None
        with lekvar.useBackend(interpreter):
            self.value = self.value.eval()

            if interpreter.State.stdout:
                print(interpreter.State.stdout, end="")

    def eval(self):
        if self.value is not None:
            return self.value
        return None

    def __repr__(self):
        return "pragma({})".format(self.value)

lekvar.Pragma = Pragma
