from ..errors import *
from .. import lekvar

class Operation(lekvar.Call):
    def verify(self):
        # Special case error reporting for operations
        try:
            lekvar.Call.verify(self)
        except TypeError as e:
            if isinstance(self.called, lekvar.Attribute):
                raise e.add(message="TODO: write this")
            elif isinstance(self.called, lekvar.Identifier):
                raise e.add(message="TODO: write this")
            raise InternalError("Unhandled type used in operation")

lekvar.Operation = Operation
