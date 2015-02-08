import unittest
from io import StringIO

from .. import tests
from . import lexer

class JamTests(unittest.TestCase):
    def test_lekxer(self):
        test = """# Foo bar
def def_end=  =return     #
defend end"""
        # Expected output token types
        expected = [
            lexer.Tokens.comment,
            lexer.Tokens.newline,
            lexer.Tokens.keyword,
            lexer.Tokens.identifier,
            lexer.Tokens.operator,
            lexer.Tokens.operator,
            lexer.Tokens.keyword,
            lexer.Tokens.comment,
            lexer.Tokens.newline,
            lexer.Tokens.identifier,
            lexer.Tokens.keyword,
        ]
        with StringIO(test) as input:
            lex = lexer.Lexer(input).lex

            # Check if the lexed output equals the expected
            for output in expected:
                self.assertEqual(lex().type, output)



