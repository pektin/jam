from enum import Enum
import string
from io import IOBase

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
WHITESPACE = set(" \t")
WORD_CHARACTERS = set(string.ascii_letters + "_")
KEYWORDS = {
    "def",
    "end",
    "return",
}

class Token:
    def __init__(self, type:Tokens, start:int, end:int, data:str = None):
        self.type = type
        self.start = start
        self.end = end
        self.data = data

class Lexer:
    source = None

    def __init__(self, source:IOBase):
        self.source = source
        self.next()

    @property
    def pos(self):
        return self.source.tell()

    current = None

    def next(self):
        self.current = self.source.read(1)

    #
    # Lexing Methods
    #

    def lex(self):
        # Ignore whitespace
        while self.current in WHITESPACE:
            self.next()

        if self.current == COMMENT_CHAR:
            return self.comment()
        elif self.current in WORD_CHARACTERS:
            return self.identifier()
        elif self.current == "\n":
            pos = self.pos
            self.next()
            return Token(Tokens.newline, pos - 1, pos)
        else:
            raise SyntaxError("Unexpected Character '{}'".format(self.current))

    def comment(self):
        start = self.pos - 1

        self.next()
        comment = self.current
        while self.current != "\n":
            comment += self.current
            self.next()


        return Token(Tokens.comment, start, self.pos, comment)

    def identifier(self):
        start = self.pos - 1
        name = self.current

        self.next()
        while self.current in WORD_CHARACTERS:
            name += self.current
            self.next()

        if name in KEYWORDS:
            return Token(Tokens.keyword, start, self.pos, name)
        else:
            return Token(Tokens.identifier, start, self.pos, name)

