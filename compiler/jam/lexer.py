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
    "group_start",
    "group_end",
    "typeof",
    "dot",
    "comma",
    "equal"
])

#
# Constants
#

COMMENT_CHAR = "#"
STRING_CHAR = "\""
WHITESPACE = set(" \t")
WORD_CHARACTERS = set(string.ascii_letters + "_")
WORD_CHARACTERS_AFTER = WORD_CHARACTERS | set(string.digits)
KEYWORDS = {
    "def",
    "end",
    "return",
    "class",
}
DIRECT_MAP = {
    "(": Tokens.group_start,
    ")": Tokens.group_end,
    ":": Tokens.typeof,
    ",": Tokens.comma,
    "=": Tokens.equal,
    ".": Tokens.dot,
}

class Token:
    def __init__(self, type:Tokens, start:int, end:int, data:str = None):
        self.type = type
        self.start = start
        self.end = end
        self.data = data

    def __repr__(self):
        return "<{}: {}>".format(self.type, self.data)

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
        elif self.current == STRING_CHAR:
            return self.string()
        elif self.current in DIRECT_MAP:
            pos = self.pos
            cu = self.current
            self.next()
            return Token(DIRECT_MAP[cu], pos - 1, pos)
        elif self.current == "\n":
            pos = self.pos
            self.next()
            return Token(Tokens.newline, pos - 1, pos)
        elif self.current == "":
            return None
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
        while self.current in WORD_CHARACTERS_AFTER:
            name += self.current
            self.next()

        if name in KEYWORDS:
            return Token(Tokens.keyword, start, self.pos, name)
        else:
            return Token(Tokens.identifier, start, self.pos, name)

    def string(self):
        start = self.pos - 1
        self.next()

        contents = ""
        while self.current != STRING_CHAR:
            contents += self.current
            self.next()
            if not self.current:
                raise SyntaxError("Expected '"' before EOF')
        self.next()

        contents = contents.encode("UTF-8").decode("unicode-escape")
        return Token(Tokens.string, start, self.pos, contents)
