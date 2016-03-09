from ..errors import *
from .. import lekvar

class Operation(lekvar.Call):
    def verify(self):
        # Special case error reporting for operations
        try:
            lekvar.Call.verify(self)
        except TypeError as e:
            if e.__traceback__.tb_frame.f_code is self.verify.__code__:
                if isinstance(self.called, lekvar.Attribute):
                    raise TypeError(message="TODO: write this")
                elif isinstance(self.called, lekvar.Identifier):
                    raise TypeError(message="TODO: write this")
            raise

lekvar.Operation = Operation
