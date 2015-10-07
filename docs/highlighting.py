from pygments.lexer import RegexLexer, bygroups, include, combined, words
from pygments.token import *
import sphinx

class JamLexer(RegexLexer):
    name = "Jam"
    aliases = ["jam"]
    filenames = ["*.jm"]

    INTEGER_REGEX = r"[0-9]([0-9_]*[0-9])?"

    tokens = {
        'root': [
            (r"#.*?$", Comment),
            include('constants'),
            include('keywords'),
            include('builtins'),
            (INTEGER_REGEX, Literal.Number),
            (r"{0}\.({0})?".format(INTEGER_REGEX), Literal.Number),
            (r"({0})?\.{0}".format(INTEGER_REGEX), Literal.Number),
            (r"\"(.*)?\"", Literal.String),
            (r"`(.*)?`", Literal.String),
            (r"\(", Text, '#push'),
            (r"\)", Text, '#pop'),
            (" ", Text.Whitespace),
            include('operators'),
            (r"([a-zA-Z_][a-zA-Z_0-9]*)", Name),
            # Mark everything unrecognised as normal
            # Catch-all for bad lexers
            (r".", Name),
        ],

        'keywords': [
            (words(
                (
                    "self",
                    "const",
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
                    "import",
                ), suffix = r'\b'),
             Keyword)
        ],

        'constants': [
            (words(
                (
                    "true",
                    "false",
                    "null",
                    "inf",
                    "nan",
                ), suffix = r'\b'),
             Name.Builtin)
        ],

        'builtins': [
            (words(
                (
                    "puts",
                    "Int",
                    "Int8",
                    "Int16",
                    "Int32",
                    "Int64",
                    "Int128",
                    "UInt",
                    "UInt8",
                    "UInt16",
                    "UInt32",
                    "UInt64",
                    "UInt128",
                    "Float",
                    "Float16",
                    "Float32",
                    "Float64",
                    "UFloat",
                    "UFloat16",
                    "UFloat32",
                    "UFloat64",
                    "Bool",
                ), suffix = r'\b'),
             Name.Builtin)
        ],

        'operators': [(symbol, Operator) for symbol in (
                r"~",
                r"!",
                r"%",
                r"\^",
                r"&",
                r"&&",
                r"\*",
                r"\*\*",
                r"-",
                r"-=",
                r"\+",
                r"\+=",
                r"=",
                r"==",
                r"!=",
                r"\|",
                r"\|\|",
                r":",
                r"\?",
                r"<",
                r"<=",
                r">",
                r">=",
                r"\.",
                r"/",
                r"//",
            )
        ]
    }
