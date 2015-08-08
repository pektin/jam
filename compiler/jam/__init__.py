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

def compile(input:IOBase, output:IOBase = None, output_ir:IOBase = None,
            logger = logging.getLogger()):

    ir = parser.parseFile(input, logger=logger)

    lekvar.verify(ir, _builtins(), logger=logger)

    llvm_ir = llvm.emit(ir, logger)
    executable = None

    if output_ir is not None:
        output_ir.write(llvm_ir)

    if output is not None:
        executable = llvm.compile(llvm_ir)
        output.write(executable)

    return llvm_ir, executable

def interpret(input:IOBase, output_ir:IOBase = None, logger = logging.getLogger()):
    llvm_ir, _ = compile(input, None, output_ir, logger)

    return llvm.run(llvm_ir).decode("UTF-8")
