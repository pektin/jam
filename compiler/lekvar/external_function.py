from ..errors import *

from .state import State
from .core import Context, Object, BoundObject, Type
from .function import Function, FunctionType

class ExternalFunction(BoundObject):
    external_name = None
    type = None

    dependent = False
    verified = False

    def __init__(self, name:str, external_name:str, arguments:[Type], return_type:Type, tokens = None):
        super().__init__(name, tokens)
        self.external_name = external_name
        self.type = FunctionType(arguments, return_type)

    def copy(self):
        raise InternalError("Not Implemented")

    def verify(self):
        if self.verified: return
        self.verified = True

        self.type.verify()

    def resolveType(self):
        return self.type

    resolveCall = Function.resolveCall

    def __repr__(self):
        return "def {}=>{} -> {}".format(self.name, self.external_name, self.type)
