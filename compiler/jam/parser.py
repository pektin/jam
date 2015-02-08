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

        value = parseLine(lexer, token)

        # EOF escape
        if value is None: break

        if isinstance(value, lekvar.Scope):
            # Scopes are automatically added as children
            children[value.name] = value
        else:
            # Other values are added as instructions
            instructions.append(value)

    return lekvar.Module( children, lekvar.Function([], instructions, None) )

def parseLine(lexer, token):
    # Parse a line. The line may not exist

    # Ignore newlines
    while token.type == Tokens.newline:
        token = lexer.lex()

        # EOF handling
        if token is None: return None

    if token.type == Tokens.comment:
        return lekvar.Comment(token.data)
    else:
        return parseValue(lexer, token)

def parseValue(lexer, token):
    # Parse for a value. The value must exist

    # Ignore comments and newlines until a value is reached
    while token.type in [Tokens.comment, Tokens.newline]:
        token = lexer.lex()

        # EOF handling
        if token is None:
            raise SyntaxError("Expected value before EOF")

    #TODO: Everything
    raise NotImplemented()
