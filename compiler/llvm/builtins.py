from ..lekvar.lekvar import *

def builtins():
    return Module("builtins", [
        ExternalFunction("print", "puts", [Reference("String")], Reference("Int32")),
        LLVMType("String"),
        LLVMType("Int8"),
        LLVMType("Int16"),
        LLVMType("Int32"),
        LLVMType("Int64"),
        LLVMType("Float16"),
        LLVMType("Float32"),
        LLVMType("Float64"),
    ], Function("main", [], [], None))

#
# Temporary
#

class LLVMType(Type):
    def __init__(self, name:str):
        super().__init__(name)

    def copy(self):
        raise InternalError("Cannot copy LLVMType")

    def verify(self):
        pass

    def resolveType(self):
        raise InternalError("Not Implemented")

    @property
    def children(self):
        raise InternalError("Not Implemented")

    def addChild(self, child):
        raise InternalError("Not Implemented")

    def checkCompatibility(self, other:Type):
        if isinstance(other, Reference):
            other = other.value

        if isinstance(other, LLVMType):
            if self.name == other.name:
                return True
        return False

    def __repr__(self):
        return "{}<{}>".format(self.__class__.__name__, self.name)

