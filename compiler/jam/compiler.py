from io import IOBase
from subprocess import check_output

from . import parser
from ..lekvar import lekvar
from ..llvm import emitter as llvm
from ..llvm.builtins import builtins
from ..errors import CompilerError

def compileRun(path:str, target:str):
    compileFile(path, target)
    return check_output(["lli", target])

def compileFile(path:str, target:str):
    with open(path, "r") as input, open(target, "w") as output:
        compile(input, output)

def compile(input:IOBase, output:IOBase):
    try:
        # Produce lekvar
        ir = parser.parseFile(input)
        lekvar.verify(ir, builtins())
        # Emit LLVM
        output.write(llvm.emit(ir).decode("UTF-8"))
    except CompilerError as err:
        input.seek(0)
        err.format(input.read())
        raise err

