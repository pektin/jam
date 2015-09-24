import io
import logging

from .. import lekvar

from . import parser

BUILTINS_PATH = "compiler/jam/builtins.jm"

BUILTINS_CACHE = open(BUILTINS_PATH, "r").read()

def builtins(logger = logging.getLogger()):
    ir = parser.parseFile(io.StringIO(BUILTINS_CACHE), logger)

    # Certain functionality cannot be built into the library
    # as it is not valid jam
    and_ = lekvar.Function("&&", [lekvar.Variable("lhs", lekvar.Reference("Bool")),
                                  lekvar.Variable("rhs", lekvar.Reference("Bool"))],
    [
        lekvar.Branch(lekvar.Reference("lhs"), [
            lekvar.Return(lekvar.Reference("rhs")),
        ], [
            lekvar.Return(lekvar.Reference("lhs")),
        ]),
    ], [])
    ir.context.addChild(and_)

    or_ = lekvar.Function("||", [lekvar.Variable("lhs", lekvar.Reference("Bool")),
                                  lekvar.Variable("rhs", lekvar.Reference("Bool"))],
    [
        lekvar.Branch(lekvar.Reference("lhs"), [
            lekvar.Return(lekvar.Reference("lhs")),
        ], [
            lekvar.Return(lekvar.Reference("rhs")),
        ]),
    ], [])
    ir.context.addChild(or_)

    return ir
