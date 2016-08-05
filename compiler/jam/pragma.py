from contextlib import ExitStack

from .. import errors
from .. import lekvar
from .. import interpreter

class Pragma(lekvar.BoundLink):
    has_run = False

    def verify(self):
        self.value.verify()

        if self.has_run: return
        self.has_run = True
        self._run()

    def _run(self):
        interpreter.State.stdout = None
        with lekvar.useBackend(interpreter):
            self.value = self.value.eval()

            if interpreter.State.stdout:
                print(interpreter.State.stdout, end="")

    def eval(self):
        pass

lekvar.Pragma = Pragma
