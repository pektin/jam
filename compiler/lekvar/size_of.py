from .core import Type
from .external_function import ExternalFunction

class SizeOf(ExternalFunction):
    def __init__(self, name:str, argument:Type, return_type:Type):
        ExternalFunction.__init__(self, name, name, [argument], return_type)
        self.argument = argument
