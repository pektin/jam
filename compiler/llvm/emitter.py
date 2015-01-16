from contextlib import contextmanager
from io import IOBase

from ..lekvar.lekvar import *
from ..lekvar.errors import *

# Temporary
LLVMMAP = {
    "String": "i8*",
    "Int": "i32",
}

class Emitter:
    output = None
    stack = None

    def __init__(self, out:IOBase):
        self.output = out
        self.stack = []

    #TODO: Emission

    def emitExternalFunction(self):
        pass

    @contextmanager
    def emitFunction(self):
        self.stack.append("")
        yield
        self.output.write(self.stack.pop())

    def emitFunctionValue(self):
        pass

    def emitLiteral(self):
        pass

    def emitCall(self):
        pass
