from io import IOBase

from .. errors import *
from ..lekvar import lekvar
from .lexer import Lexer, Tokens

#
# Setup functions
#

def parseFile(source:IOBase):
    lexer = Lexer(source)

    children = {}
    instructions = []

    while True:
        token = lexer.lex()
        # EOF escape
        if token is None: break

        value = parseValue(lexer, token)

        if isinstance(value, lekvar.Scope):
            # Scopes are automatically added as children
            children[value.name] = value
        else:
            # Other values are added as instructions
            instructions.append(value)

    return lekvar.Module( children, Function([], instructions, None) )

def parseLine(lexer, token):
    if token.type == Tokens.comment:
        return lekvar.Comment()
    else:
        return parseValue(lexer, token)

def parseValue(lexer, token):
    raise NotImplemented()
