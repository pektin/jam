from . import parser
from ..llvm.emitter import Emitter

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
        lekvar.emitDefinition(emitter)
        emitter.finalize()

    # Wait and check the output
    p.wait(10) # Arbitrary 10 second execution limit

    out, err = p.stdout.read(), p.stderr.read()
    if err:
        InternalError(err)
    p.stdout.close()
    p.stderr.close()

    return out

