import logging
import subprocess
from tempfile import NamedTemporaryFile

from .. import lekvar
from ..errors import *

from .state import State
from .builtins import builtins
from . import emitter
from . import bindings

def emit(module:lekvar.Module, logger = logging.getLogger(), opt_level = 1):
    State.logger = logger.getChild("llvm")

    with State.begin("main", logger):
        module.emit()

    State.module.verify()
    _optimise(State.module, opt_level, opt_level)
    return State.module.toString()

def _optimise(module:bindings.Module, level:int, size_level:int):
    manager = bindings.PassManager.new()
    manager.setOptLevel(level)
    manager.setOptSizeLevel(size_level)
    return bool(manager.run(module))

# Wrapping around lli
#TODO: Replace with direct calls to llvm
def run(source:bytes):
    try:
        return subprocess.check_output("lli-" + bindings.LLVM_VERSION,
            input = source,
            stderr = subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as e:
        raise ExecutionError("lli error running source: {}".format(e.output))

# Wrapping around clang
#TODO: Replace with direct calls to llvm
def compile(source:bytes):
    try:
        # Leave cleaning these up to python. Breaks circleci otherwise...
        f_in = NamedTemporaryFile('wb', suffix=".ll")
        f_in.write(source)
        f_in.flush()

        f_out = NamedTemporaryFile('rb')
        subprocess.check_output([
                "clang-" + bindings.LLVM_VERSION,
                "-v", "-o", f_out.name, f_in.name
            ], stderr = subprocess.STDOUT)
        return f_out.read()
    except subprocess.CalledProcessError as e:
        output = e.output.decode("UTF-8")
        raise ExecutionError("clang error compiling source {}".format(output))
