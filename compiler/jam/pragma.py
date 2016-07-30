from .. import errors
from .. import lekvar
from .. import interpreter

class Pragma(lekvar.BoundLink):
    def verify(self):
        self.value.verify()

        with lekvar.useBackend(interpreter):
            self.value = self.value.eval()
            print(interpreter.State.stdout, end="")

lekvar.Pragma = Pragma
