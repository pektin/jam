from . import parser
from ..lekvar import lekvar
from ..llvm import emitter as llvm

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
    ir = parser.parseFile(input)
    lekvar.verify(ir)
    # Emit LLVM
    output.write(llvm.emit(ir).decode("UTF-8"))

