import sys
from io import StringIO

import pytest
import logging

from .. import jam, lekvar, llvm

from .lexer import Tokens, Lexer

def test_lexer():
    test = """# def:end )=
def :def_end=new  (return(a)  #
    if=else-78_788_934_0 ///*
  ===<=>=<>!=
defend+_- end"""
    # Expected output token types
    expected = [
        Tokens.comment,

        Tokens.def_kwd,
        Tokens.typeof,
        Tokens.identifier,
        Tokens.equal,
        Tokens.new_kwd,
        Tokens.group_start,
        Tokens.return_kwd,
        Tokens.group_start,
        Tokens.identifier,
        Tokens.group_end,
        Tokens.comment,

        Tokens.if_kwd,
        Tokens.equal,
        Tokens.else_kwd,
        Tokens.subtraction,
        Tokens.integer,
        Tokens.integer_division,
        Tokens.division,
        Tokens.multiplication,

        Tokens.equality,
        Tokens.equal,
        Tokens.smaller_than_or_equal_to,
        Tokens.greater_than_or_equal_to,
        Tokens.smaller_than,
        Tokens.greater_than,
        Tokens.inequality,

        Tokens.identifier,
        Tokens.addition,
        Tokens.identifier,
        Tokens.subtraction,
        Tokens.end_kwd,
    ]
    with StringIO(test) as input:
        lex = Lexer(input).lex
        # Check if the lexed output equals the expected
        for output in expected:
            token = lex()
            assert token is not None
            assert token.type == output

def test_builtin_lib(verbosity):
    logging.basicConfig(level=logging.WARNING - verbosity*10, stream=sys.stdout)

    ir = jam.builtins()
    ir.context.addChild(llvm.builtins())

    lekvar.verify(ir, ir)

    #TODO: Make this work
    #module = llvm.emit(ir)
