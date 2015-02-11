from . import parser
from ..llvm.emitter import Emitter

from io import IOBase
from subprocess import check_output

def compileRun(path:str, target:str):
    compileFile(path, target)
    return check_output(["lli", target])

def compileFile(path:str, target:str):
    with open(path, "r") as input, open(target, "w") as output:
        compile(input, output)

def compile(input:IOBase, output:IOBase):
    # Produce lekvar
    lekvar = parser.parseFile(input)
    lekvar.verify()
    # Emit LLVM
    emitter = Emitter(output)
    lekvar.emitDefinition(emitter)
    emitter.finalize()

