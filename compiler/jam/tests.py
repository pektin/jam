import sys
from io import StringIO

import pytest
import logging

from . import lexer
from . import parser
from . import compiler
from .. import lekvar
from ..llvm import emitter as llvm
from ..llvm.builtins import builtins

BUILTIN = "compiler/jam/builtins.jm"

def test_lexer():
    test = """# def:end )=
def :def_end=new  (return(a)  #
    if=else-78_788_934_0 ///*
  ===<=>=<>!=
defend+_- end"""
    # Expected output token types
    expected = [
        lexer.Tokens.comment,

        lexer.Tokens.def_kwd,
        lexer.Tokens.typeof,
        lexer.Tokens.identifier,
        lexer.Tokens.equal,
        lexer.Tokens.new_kwd,
        lexer.Tokens.group_start,
        lexer.Tokens.return_kwd,
        lexer.Tokens.group_start,
        lexer.Tokens.identifier,
        lexer.Tokens.group_end,
        lexer.Tokens.comment,

        lexer.Tokens.if_kwd,
        lexer.Tokens.equal,
        lexer.Tokens.else_kwd,
        lexer.Tokens.subtraction,
        lexer.Tokens.integer,
        lexer.Tokens.integer_division,
        lexer.Tokens.division,
        lexer.Tokens.multiplication,

        lexer.Tokens.equality,
        lexer.Tokens.equal,
        lexer.Tokens.smaller_than_or_equal_to,
        lexer.Tokens.greater_than_or_equal_to,
        lexer.Tokens.smaller_than,
        lexer.Tokens.greater_than,
        lexer.Tokens.inequality,

        lexer.Tokens.identifier,
        lexer.Tokens.addition,
        lexer.Tokens.identifier,
        lexer.Tokens.subtraction,
        lexer.Tokens.end_kwd,
    ]
    with StringIO(test) as input:
        lex = lexer.Lexer(input).lex
        # Check if the lexed output equals the expected
        for output in expected:
            token = lex()
            assert token is not None
            assert token.type == output

def test_builtin_lib(verbosity):
    logging.basicConfig(level=logging.WARNING - verbosity*10, stream=sys.stdout)

    ir = compiler.builtins()

    lekvar.verify(ir, ir)

    #TODO: Make this work
    #module = llvm.emit(ir)
