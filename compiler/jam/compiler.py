from .jam import parser
from .llvm.emitter import Emitter

from subprocess import Popen, PIPE

def compileRun(path:str):
    # Parse source and generate lekvar
    with open(path, "r") as f:
        lekvar = parser.parseFile(f)
    lekvar.verify()

    # Emit and interpet LLVM bytecode
    p = Popen("lli", stdin=PIPE, stdout=PIPE, stderr=PIPE)
    with p.stdin as input:
        emitter = Emitter(input)
        lekvar.emit(emitter)
        emitter.finalize()

    # Wait and check the output
    p.wait(10)
    out, err = p.communicate()
    if err:
        InternalError(err)

    return out

