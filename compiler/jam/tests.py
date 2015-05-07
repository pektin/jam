from io import StringIO

import pytest

from . import lexer
from . import parser
from ..lekvar import lekvar
from ..llvm import emitter as llvm
from ..llvm.builtins import builtins

BUILTIN = "compiler/jam/builtins.jm"

def test_lexer():
    test = """# def:end )=
def :def_end=  (=return(a)  78_788_934_0   #
defend+_- end"""
    # Expected output token types
    expected = [
        lexer.Tokens.comment,
        lexer.Tokens.newline,

        lexer.Tokens.def_kwd,
        lexer.Tokens.typeof,
        lexer.Tokens.identifier,
        lexer.Tokens.equal,
        lexer.Tokens.group_start,
        lexer.Tokens.equal,
        lexer.Tokens.return_kwd,
        lexer.Tokens.group_start,
        lexer.Tokens.identifier,
        lexer.Tokens.group_end,
        lexer.Tokens.integer,
        lexer.Tokens.comment,
        lexer.Tokens.newline,

        lexer.Tokens.identifier,
        lexer.Tokens.plus,
        lexer.Tokens.identifier,
        lexer.Tokens.minus,
        lexer.Tokens.end_kwd,
    ]
    with StringIO(test) as input:
        lex = lexer.Lexer(input).lex
        # Check if the lexed output equals the expected
        for output in expected:
            token = lex()
            assert token is not None
            assert token.type == output

def test_builtin_lib():
    with open(BUILTIN, "r") as f:
        ir = parser.parseFile(f)

    # inject _builtins module
    ir.context.addChild(builtins())

    # Use module as builtin module as well
    lekvar.verify(ir, ir)

    module = llvm.emit(ir)
