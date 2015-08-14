import logging

from .. import lekvar

from . import parser

BUILTINS_PATH = "compiler/jam/builtins.jm"

def builtins(logger = logging.getLogger()):
    ir = parser.parseFile(open(BUILTINS_PATH, "r"), logger)
    return ir
