from ..lekvar.lekvar import *

def builtins():
    return Module("main", [
        ExternalFunction("print", "puts", [Reference("String")], Reference("Int"))
    ], Function("main", [], [], None))
