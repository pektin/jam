import io
import logging
from os import path

from .. import lekvar

from . import parser

BUILTINS_FILE = "builtins.jm"
BUILTINS_PATH = path.join(path.split(__file__)[0], BUILTINS_FILE)

BUILTINS_CACHE = open(BUILTINS_PATH, "r").read()

def builtins(logger = logging.getLogger()):
    ir = parser.parseFile(io.StringIO(BUILTINS_CACHE), logger)

    # Certain functions cannot be built into the library
    # as they cannot be expressed in jam syntax
    and_ = lekvar.Function("&&", [lekvar.Variable("lhs", lekvar.Reference("Bool")),
                                  lekvar.Variable("rhs", lekvar.Reference("Bool"))],
    [
        lekvar.Branch(lekvar.Reference("lhs"), [
            lekvar.Return(lekvar.Reference("rhs")),
        ], lekvar.Branch(None, [
            lekvar.Return(lekvar.Reference("lhs")),
        ])),
    ], [])
    ir.context.addChild(and_)

    or_ = lekvar.Function("||", [lekvar.Variable("lhs", lekvar.Reference("Bool")),
                                  lekvar.Variable("rhs", lekvar.Reference("Bool"))],
    [
        lekvar.Branch(lekvar.Reference("lhs"), [
            lekvar.Return(lekvar.Reference("lhs")),
        ], lekvar.Branch(None, [
            lekvar.Return(lekvar.Reference("rhs")),
        ])),
    ], [])
    ir.context.addChild(or_)

    return ir
