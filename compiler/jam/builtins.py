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

    with open(BUILTINS_PATH, 'r') as f:
        # Use StringIO because other files can't be pickled
        ir = parser.parseFile(io.StringIO(f.read()), logger)

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

    global builtin_cache
    builtin_cache = pickle.dumps(ir)

    return ir
