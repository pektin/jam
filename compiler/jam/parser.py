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

    def _unexpected(self, token):
        raise SyntaxError("Unexpected {}: '{}'".format(token.type, token.data))

    def strip(self, types:[Tokens] = [Tokens.newline]):
        # Strip all tokens of a type, returning one lookAhead or None
        token = self.lookAhead()
        while token.type in types:
            self.next()
            token = self.lookAhead()
            if token is None: return None
        return token

    def expect(self, type:Tokens = Tokens.identifier):
        # Parse for an expected token, returning it's data
        token = self.next()
        if token.type != type:
            self._unexpected(token)
        return token.data

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

        # Ignore newlines
        token = self.strip()
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
        token = self.strip([Tokens.comment, Tokens.newline])
        # EOF handling
        if token is None:
            raise SyntaxError("Expected value before EOF")

        # Identify the kind of value
        if token.type == Tokens.keyword:
            if token.data == "def":
                return self.parseFunction()
        elif token.type == Tokens.identifier:
            if self.lookAhead(2).type == Tokens.group_start:
                return self.parseCall()
            else:
                return lekvar.Reference(self.next().data)

        self._unexpected(token)

    def parseFunction(self):
        # "def" should have already been identified
        self.next()

        name = self.expect()

        arguments = []

        token = self.lookAhead()
        if token.type != Tokens.newline and token.type != Tokens.typeof: # Allow for no arguments
            token = self.next()

            # Arguments start with "("
            if token.type != Tokens.group_start:
                self._unexpected(token)

            if self.lookAhead().type != Tokens.group_end: # Allow for no arguments

                # Parse arguments
                while True:
                    arguments.append(self.parseVariable())

                    token = self.next()
                    # Arguments separated by comma
                    if token.type == Tokens.comma:
                        continue
                    # Arguments end with ")"
                    elif token.type == Tokens.group_end:
                        break
                    else:
                        self._unexpected(token)
            else:
                self.next()

        return_type = self.parseTypeSig()

        instructions = []

        # Parse instructions
        while True:
            token = self.strip()

            if token is None:
                raise SyntaxError("Expected 'end' before EOF")

            if token.type == Tokens.keyword:
                if token.data == "end":
                    return Function(name, arguments, return_type, instructions)
            instructions.append(self.parseLine())

    def parseVariable(self):
        # Parse a variable, with optional type signature

        name = self.expect()
        type = self.parseTypeSig()

        return lekvar.Variable(name, type)

    def parseTypeSig(self):
        # Parse an optional type signature
        if self.lookAhead().type != Tokens.typeof:
            return None

        self.next()
        return self.expect()
