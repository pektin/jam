import logging
from io import IOBase

from . import parser
from .. import lekvar
from ..llvm import emitter as llvm
from ..llvm.builtins import builtins
from ..errors import CompilerError

llvm.builtins = builtins

BUILTINS = "compiler/jam/builtins.jm"

def builtins():
    with open(BUILTINS, "r") as f:
        ir = parser.parseFile(f)

    # Inject backend builtins into frontend builtins (there may be a better method?)
    ir.context.addChild(llvm.builtins())

    return ir

def _compile(input:IOBase, logger):
    # Produce lekvar
    ir = parser.parseFile(input)
    lekvar.verify(ir, builtins(), logger=logger, source=input)
    # Emit LLVM
    return llvm.emit(ir, logger)

def compileRun(input:IOBase, output:IOBase = None, logger = logging.getLogger()):
    source = _compile(input, logger)
    if output is not None:
        output.write(source.decode("UTF-8"))
    return llvm.run(source).decode("UTF-8")

def compile(input:IOBase, output:IOBase, logger = logging.getLogger()):
    output.write(_compile(input, logger).decode("UTF-8"))


