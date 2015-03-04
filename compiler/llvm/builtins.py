from ..lekvar.lekvar import *

def builtins():
    return Builtins({
        "print": ExternalFunction("print", "puts", [LLVMType("String")], LLVMType("Int"))
    })
