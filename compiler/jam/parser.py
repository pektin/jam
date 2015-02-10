from io import IOBase

from .. errors import *
from ..lekvar import lekvar
from .lexer import Lexer, Tokens

#
# Setup functions
#

def parseFile(source:IOBase):
    return Parser(Lexer(source)).parseModule()

class Parser:
    lexer = None
    tokens = None

    def __init__(self, lexer):
        self.lexer = lexer
        self.tokens = []

    def next(self):
        if len(self.tokens) == 0:
            return self.lexer.lex()
        else:
            return self.tokens.pop(0)

    def lookAhead(self, num = 1):
        while len(self.tokens) < num:
            self.tokens.append(self.lexer.lex())
        return self.tokens[-1]

    def parseModule(self):
        children = {}
        instructions = []

        while True:
            value = self.parseLine()

            # EOF escape
            if value is None: break

            if isinstance(value, lekvar.Scope):
                # Scopes are automatically added as children
                children[value.name] = value
            else:
                # Other values are added as instructions
                instructions.append(value)

        return lekvar.Module(children,
               lekvar.Function([], instructions, None))

    def parseLine(self):
        # Parse a line. The line may not exist

        token = self.lookAhead()

        # Ignore newlines
        while token.type == Tokens.newline:
            self.next()
            token = self.lookAhead()

            # EOF handling
            if token is None: return None

        if token.type == Tokens.comment:
            return lekvar.Comment(self.next().data)
        elif token.type == Tokens.keyword:
            if token.data == "return":
                return self.parseReturn()
        return self.parseValue()

    def parseValue(self):
        # Parse for a value. The value is expected to exist

        token = self.lookAhead()

        # Ignore comments and newlines until a value is reached
        while token.type in [Tokens.comment, Tokens.newline]:
            self.next()
            token = self.lookAhead()

            # EOF handling
            if token is None:
                raise SyntaxError("Expected value before EOF")

        # Identify the kind of value
        if token.type == Tokens.keyword:
            if token.data == "def":
                return self.parseMethod()
        elif token.type == Tokens.identifier:
            if self.lookAhead(2).type == Tokens.group_start:
                return self.parseCall()
            else:
                return lekvar.Reference(self.next().data)

        raise SyntaxError("Unexpected {}: '{}'".format(token.type, token.data))
