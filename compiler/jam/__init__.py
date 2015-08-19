import logging
from io import IOBase

from . import lexer
from . import parser
from .builtins import builtins
# Lekvar extensions
from . import import_

def parse(input:IOBase, logger = logging.getLogger()):
    return parser.parseFile(input, logger=logger)
