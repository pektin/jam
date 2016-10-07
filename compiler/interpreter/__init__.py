import logging
from io import StringIO
from contextlib import redirect_stdout

from . builtins import builtins
from .state import State
from . import runner

def run(module, logger = logging.getLogger(), opt_level = 0):
    #logger = logger.getChild("interpreter")
    State.stdout = ""

    module.eval()

    return State.stdout.encode("UTF-8")
