from ..lekvar.lekvar import *

def builtins():
    return Module("main", {
        "print": ExternalFunction("print", "puts", [Reference("String")], Reference("Int"))
    }, Function("main", [], [], None))
