from ..errors import *

from ..lekvar.links import Link
from .. import lekvar

class Import(Link):
    path = None

    def __init__(self, path:[str], name:str = None, tokens = None):
        if name is None:
            name = path[-1]
        super().__init__(name, None, tokens)
        self.path = path

    def copy(self):
        raise InternalError("Not Implemented")

    def verify(self):
        raise InternalError("Not Implemented")

lekvar.Import = Import
