from pygments.lexer import RegexLexer, bygroups, include, combined
from pygments.token import *
import sphinx

class JamLexer(RegexLexer):
    name = "Jam"
    aliases = ["jam"]
    filenames = ["*.jm"]

    INTEGER_REGEX = "[0-9]([0-9_]*[0-9])?"

    tokens = {
        'root': [
            ("#.*?$", Comment),
            include('keywords'),
            ("true", Name.Builtin),
            ("false", Name.Builtin),
            ("null", Name.Builtin),
            (INTEGER_REGEX, Literal.Number),
            ("{0}\.({0})?".format(INTEGER_REGEX), Literal.Number),
            ("({0})?\.{0}".format(INTEGER_REGEX), Literal.Number),
            ("\"(.*)?\"", Literal.String),
            ("\(", Text, '#push'),
            ("\)", Text, '#pop'),
            (" ", Text.Whitespace),
            include('operators'),
            ("([a-zA-Z_][a-zA-Z_0-9]*)", Name),
        ],

        'keywords': [(i, Keyword) for i in [
            "end",
            "def",
            "class",
            "template",
            "if",
            "elif",
            "else",
            "while",
            "for",
            "in",
            "as",
        ]],

        'operators': [(i, Operator) for i in [
            "~",
            "~",
            "!",
            "%",
            "\^",
            "&",
            "&&",
            "\*",
            "\*\*",
            "-",
            "-=",
            "\+",
            "\+=",
            "=",
            "==",
            "!=",
            "\|",
            "\|\|",
            ":",
            "\?",
            "<",
            "<=",
            ">",
            ">=",
            "\.",
            "/",
            "//",
        ]],
    }
