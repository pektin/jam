from enum import Enum

from ..errors import *

Tokens = Enum("Tokens", [
    "comment"
    "identifier"
    "keyword"
    "string"
])

#
# Constants
#

COMMENT_CHAR = "#"

class Token:
    def __init__(self, type:Tokens, start:int, end:int, data:str):
        self.type = type
        self.start = start
        self.end = end
        self.data = data

class Lexer:
    source = None

    def __init__(self, source:file):
        self.source = source

    @property
    def pos(self):ok
        return source.tell()

    def read(self):
        return source.read(1)

    #
    # Lexing Methods
    #

    def next(self):
        current = self.pop()

        if current == COMMENT_CHAR:
            return self.comment()
        else:
            raise SyntaxError("Unexpected Character '{}'".format(current))

    def comment(self):
        start = self.pos - 1

        comment = self.pop()
        while comment[-1] != "\n":
            comment += self.pop()

        return Token(Tokens.comment, start, self.pos - 1, comment)

