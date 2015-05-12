from enum import Enum
import string
from io import IOBase

from ..errors import *

#
# Constants
#

Node = None
class Node:
    links = None
    token_type = None
    verify = None

    def __init__(self, links:[(Node, "func"),] = None, token_type = None, verify = None):
        links = links or []
        self.links = links
        self.token_type = token_type
        self.verify = verify

    def evaluate(self, character):
        out = []
        for target, condition in self.links:
            if condition(character):
                out.append(target)
        return out

    def getToken(self, start, stop, value):
        if self.verify is not None:
            value = self.verify(value)

        if self.token_type is not None:
            return Token(self.token_type, start, stop, value)
        return None

    def __repr__(self):
        return "Node(token:{})".format(self.token_type, self.links)

Tokens = Enum("Tokens", [
    "comment",

    "identifier",
    "def_kwd",
    "end_kwd",
    "return_kwd",
    "class_kwd",
    "as_kwd",
    "module_kwd",
    "self_kwd",

    "string",
    "integer",
    "newline",
    "group_start",
    "group_end",
    "typeof",
    "returns",
    "dot",
    "comma",
    "equal",

    "addition",
    "subtraction",
    "multiplication",
    "integer_division",
    "division",
])

TREE = Node()
NEWLINE_CHAR = "\n"

# Ignore whitespace
WHITESPACE = set(" \t")

TREE.links.append((TREE, lambda c: c in WHITESPACE))

# Comments
COMMENT_CHAR = "#"

node = Node(token_type=Tokens.comment)
TREE.links.append((node, lambda c: c == COMMENT_CHAR))
node.links.append((node, lambda c: c != NEWLINE_CHAR))

# Strings
FORMAT_STRING_CHAR = "\""

node = Node()
TREE.links.append((node, lambda c: c == FORMAT_STRING_CHAR))
node.links.append((node, lambda c: c != FORMAT_STRING_CHAR))
end_node = Node(token_type=Tokens.string, verify=lambda s: s[1:-1])
node.links.append((end_node, lambda c: c == FORMAT_STRING_CHAR))

# WYSIWYG Strings
WYSIWYG_STRING_CHAR = "`"

node = Node()
TREE.links.append((node, lambda c: c == WYSIWYG_STRING_CHAR))
node.links.append((node, lambda c: c != WYSIWYG_STRING_CHAR))
end_node = Node(token_type=Tokens.string, verify=lambda s: s[1:-1])
node.links.append((end_node, lambda c: c == WYSIWYG_STRING_CHAR))

# Direct maps
# Must be ordered by length for duplicated characters
DIRECT_MAP = [
    ("\n", Tokens.newline),
    ("(", Tokens.group_start),
    (")", Tokens.group_end),
    (":", Tokens.typeof),
    ("->", Tokens.returns),
    (",", Tokens.comma),
    ("=", Tokens.equal),
    (".", Tokens.dot),

    ("+", Tokens.addition),
    ("-", Tokens.subtraction),
    ("*", Tokens.multiplication),
    ("//", Tokens.integer_division),
    ("/", Tokens.division),

    ("def", Tokens.def_kwd),
    ("end", Tokens.end_kwd),
    ("return", Tokens.return_kwd),
    ("class", Tokens.class_kwd),
    ("as", Tokens.as_kwd),
    ("module", Tokens.module_kwd),
    ("self", Tokens.self_kwd),
]

for value, token_type in DIRECT_MAP:
    node = TREE
    for char in value:
        next_node = Node()
        node.links.append((next_node, lambda c, char=char: c == char))
        node = next_node
    node.token_type = token_type

# Identifiers
WORD_CHARACTERS = set(string.ascii_letters + "_")
WORD_CHARACTERS_AFTER = WORD_CHARACTERS | set(string.digits)

node = Node(token_type=Tokens.identifier)
TREE.links.append((node, lambda c: c in WORD_CHARACTERS))
end_node = Node(token_type=Tokens.identifier)
node.links.append((end_node, lambda c: c in WORD_CHARACTERS_AFTER))
end_node.links.append((end_node, lambda c: c in WORD_CHARACTERS_AFTER))

# Numbers
DIGIT_CHARACTERS = set(string.digits)

node = Node(token_type=Tokens.integer)
TREE.links.append((node, lambda c: c in DIGIT_CHARACTERS))
underscore_node = Node()
node.links.append((underscore_node, lambda c: c == "_"))
end_node = Node(token_type=Tokens.integer)
underscore_node.links.append((end_node, lambda c: c in DIGIT_CHARACTERS))
node.links.append((end_node, lambda c: c in DIGIT_CHARACTERS))
end_node.links.append((underscore_node, lambda c: c == "_"))
end_node.links.append((end_node, lambda c: c in DIGIT_CHARACTERS))

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
        token_start = self.pos
        token_data = ""
        current_nodes = [TREE]

        while True:
            next_nodes = []

            if self.current is not None:
                for node in current_nodes:
                    next_nodes += node.evaluate(self.current)

            if len(next_nodes) == 0:
                if len(current_nodes) > 0:
                    return self.outputNode(current_nodes, token_start, token_data)
                raise InternalError("Zero current nodes in lex tree.")

            elif len(next_nodes) == 1 and next_nodes[0] is TREE:
                # Restart
                token_start = self.pos
                token_data = ""
                current_nodes = [TREE]
            else:
                token_data += self.current
            self.next()

            current_nodes = next_nodes
        return None

    def outputNode(self, nodes, start, data):
        for node in nodes:
            if node.token_type is not None:
                return node.getToken(start, self.pos - 1, data)
            elif node is TREE and not self.current:
                return None
        raise SyntaxError("Unexpected Character '{}'".format(self.current), [Token(None, self.pos - 1, self.pos, self.current)])
