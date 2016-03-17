import io
import pickle
import logging
from os import path

from .. import lekvar

from . import parser

BUILTINS_FILE = "builtins.jm"
BUILTINS_PATH = path.join(path.split(__file__)[0], BUILTINS_FILE)

builtin_cache = None

# Builtins uses the pickling module
# to avoid parsing the builtin file more than once
def builtins(logger = logging.getLogger()):
    if builtin_cache is not None:
        return pickle.loads(builtin_cache)

    with open(BUILTINS_PATH, 'r') as f, lekvar.State.ioSource(io.StringIO(f.read())) as f:
        # Use StringIO because other files can't be pickled
        ir = parser.parseFile(f, logger)

        # Certain functions cannot be built into the library
        # as they cannot be expressed in jam syntax
        and_ = lekvar.Function("&&", [lekvar.Variable("lhs", lekvar.Identifier("Bool")),
                                      lekvar.Variable("rhs", lekvar.Identifier("Bool"))],
            [
                lekvar.Branch(lekvar.Identifier("lhs"), [
                    lekvar.Return(lekvar.Identifier("rhs")),
                ], lekvar.Branch(None, [
                    lekvar.Return(lekvar.Identifier("lhs")),
                ])),
            ], [])
        ir.context.addChild(and_)

        or_ = lekvar.Function("||", [lekvar.Variable("lhs", lekvar.Identifier("Bool")),
                                      lekvar.Variable("rhs", lekvar.Identifier("Bool"))],
            [
                lekvar.Branch(lekvar.Identifier("lhs"), [
                    lekvar.Return(lekvar.Identifier("lhs")),
                ], lekvar.Branch(None, [
                    lekvar.Return(lekvar.Identifier("rhs")),
                ])),
            ], [])
        ir.context.addChild(or_)

    global builtin_cache
    builtin_cache = pickle.dumps(ir)

    return ir
