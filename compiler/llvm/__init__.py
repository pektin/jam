import logging
import subprocess

from .. import lekvar
from ..errors import *

from .state import State
from .builtins import builtins
from . import emitter
from . import bindings

def emit(module:lekvar.Module, logger = logging.getLogger()):
    State.logger = logger.getChild("llvm")

    with State.begin("main", logger):
        module.emit()

    State.module.verify()
    return State.module.toString()

# Wrapping around lli
#TODO: Replace with direct calls to llvm
def run(source:bytes):
    try:
        return subprocess.check_output("lli",
            input = source,
            stderr = subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as e:
        raise ExecutionError("lli error running source: {}".format(e.output))

# Wrapping around llc
#TODO: Replace with direct calls to llvm
def compile(source:bytes):
    try:
        return subprocess.check_output(
            ["llc", "-filetype=obj"],
            input = source,
            stderr = subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as e:
        raise CompilerError("llc error compiling source {}".format(e.output))
