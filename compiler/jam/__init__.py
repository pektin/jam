import logging
from io import IOBase

from . import lexer
from . import parser
from .. import lekvar
from .. import llvm
from ..errors import CompilerError

BUILTINS = "compiler/jam/builtins.jm"

def _builtins():
    with open(BUILTINS, "r") as f, lekvar.source(f):
        ir = parser.parseFile(f)

    # Inject backend builtins into frontend builtins (there may be a better method?)
    ir.context.addChild(llvm.builtins())

    return ir

def parse(input:IOBase, logger = logging.getLogger()):
    ir = parser.parseFile(input, logger=logger)

    lekvar.verify(ir, _builtins(), logger=logger)

    return ir
