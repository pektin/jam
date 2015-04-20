from enum import Enum
import string
from io import IOBase

from ..errors import *

#
# Constants
#

Tokens = Enum("Tokens", [
    "comment",

    "identifier",
    "def_kwd",
    "end_kwd",
    "return_kwd",
    "class_kwd",
    "as_kwd",
    "module_kwd",

    "string",
    "newline",
    "group_start",
    "group_end",
    "typeof",
    "dot",
    "comma",
    "equal",

    "plus",
    "minus",
])

COMMENT_CHAR = "#"
FORMAT_STRING_CHAR = "\""
WYSIWYG_STRING_CHAR = "`"
WHITESPACE = set(" \t")
WORD_CHARACTERS = set(string.ascii_letters + "_")
WORD_CHARACTERS_AFTER = WORD_CHARACTERS | set(string.digits)
DIRECT_MAP = {
    "\n": Tokens.newline,
    "(": Tokens.group_start,
    ")": Tokens.group_end,
    ":": Tokens.typeof,
    ",": Tokens.comma,
    "=": Tokens.equal,
    ".": Tokens.dot,

    "+": Tokens.plus,
    "-": Tokens.minus,

    "def": Tokens.def_kwd,
    "end": Tokens.end_kwd,
    "return": Tokens.return_kwd,
    "class": Tokens.class_kwd,
    "as": Tokens.as_kwd,
    "module": Tokens.module_kwd,
}

#
# Lexer
#

class Token:
    def __init__(self, type:Tokens, start:int, end:int, data:str = None):
        self.type = type
        self.start = start
        self.end = end
        self.data = data

    def __repr__(self):
        if self.data is None:
            return str(self.type)
        return "{}({})".format(self.type, self.data)

class Lexer:
    source = None
    current = None

    def __init__(self, source:IOBase):
        self.source = source
        self.next()

    # Read the next character into current
    def next(self):
        self.current = self.source.read(1)

    # Returns the current position in source
    @property
    def pos(self):
        return self.source.tell()

    #
    # Lexing Methods
    #

    # Lex a single token
    def lex(self):
        # Ignore whitespace
        while self.current in WHITESPACE:
            self.next()

        # Identify the kind of token
        if self.current == COMMENT_CHAR:
            return self.comment()

        elif self.current in WORD_CHARACTERS:
            return self.identifier()

        elif self.current in [FORMAT_STRING_CHAR, WYSIWYG_STRING_CHAR]:
            return self.string()
        # Directly map a single character to a token
        elif self.current in DIRECT_MAP:
            pos = self.pos
            cu = self.current
            self.next()
            return Token(DIRECT_MAP[cu], pos - 1, pos)

        elif self.current == "":
            return None

        else:
            raise SyntaxError("Unexpected Character '{}'".format(self.current))

    # Lex a comment
    def comment(self):
        start = self.pos - 1

        # Continue until the end of the line
        comment = ""
        while self.current != "\n":
            comment += self.current
            self.next()

        return Token(Tokens.comment, start, self.pos, comment)

    # Lex an identifier
    def identifier(self):
        start = self.pos - 1

        # Continue until a non-word character is encountered
        name = ""
        while self.current in WORD_CHARACTERS_AFTER:
            name += self.current
            self.next()

        # Return specific keyword tokens if the identifier matches a keyword
        if name in DIRECT_MAP:
            return Token(DIRECT_MAP[name], start, self.pos)
        else:
            return Token(Tokens.identifier, start, self.pos, name)

    # Lex a string
    def string(self):
        start = self.pos - 1

        # Get the string type
        quote = self.current
        self.next()

        # Continue until the end quote
        contents = ""
        while self.current != quote:
            contents += self.current
            self.next()

            # Enforce that strings end before EOF
            if not self.current:
                raise SyntaxError("Expected '{}' before EOF").format(quote)

        # Ignore the last quote
        self.next()

        # Evaluate string escapes
        contents = contents.encode("UTF-8").decode("unicode-escape")

        return Token(Tokens.string, start, self.pos, contents)
