from ..lekvar.lekvar import *

def builtins():
    return Module("builtins", [
        ExternalFunction("print", "puts", [Reference("String")], Reference("Int32")),
        LLVMType("String"),
        LLVMType("Int32"),
    ], Function("main", [], [], None))

#
# Temporary
#

class LLVMType(Type):
    def __init__(self, name:str):
        super().__init__(name)

    def verify(self, scope:Scope):
        pass

    def resolveType(self, scope:Scope):
        raise InternalError("Not Implemented")

    @property
    def children(self):
        raise InternalError("Not Implemented")

    def addChild(self, child):
        raise InternalError("Not Implemented")

    def checkCompatibility(self, scope:Scope, other:Type):
        if isinstance(other, Reference):
            other = other.value

        if isinstance(other, LLVMType):
            if self.name == other.name:
                return True
        return False

    def __repr__(self):
        return "{}<{}>".format(self.__class__.__name__, self.name)

