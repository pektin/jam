from enum import Enum

from ..errors import *

Tokens = Enum("Tokens", [
    "comment",
    "identifier",
    "keyword",
    "string",
    "newline",
])

#
# Constants
#

COMMENT_CHAR = "#"

class Token:
    def __init__(self, type:Tokens, start:int, end:int, data:str = None):
        self.type = type
        self.start = start
        self.end = end
        self.data = data

class Lexer:
    source = None

    def __init__(self, source:file):
        self.source = source

    @property
    def pos(self):
        return source.tell()

    current = None

    def next(self):
        self.current = source.read(1)

    #
    # Lexing Methods
    #

    def lex(self):
        self.next()

        if self.current == COMMENT_CHAR:
            return self.comment()
        elif self.current == "\n":
            return Token(Tokens.newline, self.pos - 1, self.pos)
        else:
            raise SyntaxError("Unexpected Character '{}'".format(self.current))

    def comment(self):
        start = self.pos - 1

        self.next()
        comment = self.current
        while comment[-1] != "\n":
            comment += self.pop()

        return Token(Tokens.comment, start, self.pos, comment)

