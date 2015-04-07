from io import StringIO

from . import lexer

def test_lekxer():
    test = """# def:end )=
def :def_end=  (=return()     #
defend end"""
    # Expected output token types
    expected = [
        lexer.Tokens.comment,
        lexer.Tokens.newline,

        lexer.Tokens.keyword,
        lexer.Tokens.typeof,
        lexer.Tokens.identifier,
        lexer.Tokens.equal,
        lexer.Tokens.group_start,
        lexer.Tokens.equal,
        lexer.Tokens.keyword,
        lexer.Tokens.group_start,
        lexer.Tokens.group_end,
        lexer.Tokens.comment,
        lexer.Tokens.newline,

        lexer.Tokens.identifier,
        lexer.Tokens.keyword,
    ]
    with StringIO(test) as input:
        lex = lexer.Lexer(input).lex

        # Check if the lexed output equals the expected
        for output in expected:
            assert lex().type == output
