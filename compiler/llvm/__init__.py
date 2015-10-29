import os
import uuid
import logging
import subprocess
from tempfile import TemporaryDirectory

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

def _get_tempname(suffix = ""):
    name = str(uuid.uuid4())
    # Make sure it doesn't already exist. REALLY make sure
    while os.path.isfile(name + suffix):
        name = str(uuid.uuid4())
    return name + suffix

# Wrapping around lli
#TODO: Replace with direct calls to llvm
def run(source:bytes):
    try:
        return subprocess.check_output(bindings.LLI,
            input = source,
            stderr = subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as e:
        raise ExecutionError("lli error running source: {}".format(e.output))

# Wrapping around clang
#TODO: Replace with direct calls to llvm
def compile(source:bytes):
    with TemporaryDirectory() as build_dir:
        try:
            # Leave cleaning these up to python.
            # They should get removed by the temporary dir anyway
            path = os.path.join(build_dir, _get_tempname(suffix=".ll"))
            f_in = open(path, 'wb')
            f_in.write(source)
            f_in.flush()

            out_name = os.path.join(build_dir, _get_tempname())
            subprocess.check_output([
                    bindings.CLANG,
                    "-v", "-o", out_name, f_in.name
                ], stderr = subprocess.STDOUT)
            return open(out_name, 'rb').read()
        except subprocess.CalledProcessError as e:
            output = e.output.decode("UTF-8")
            raise ExecutionError("clang error compiling source {}".format(output))
