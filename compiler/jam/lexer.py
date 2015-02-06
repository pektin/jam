from enum import Enum

Tokens = Enum("Tokens", [
    "comment"
    "identifier"
    "keyword"
    "string"
])

class Token:
    def __init__(self, type:Tokens, start:int, end:int, data:str):
        self.type = type
        self.start = start
        self.end = end
        self.data = data

class Lexer:
    source = None

    def __init__(self, source:file):
        self.source = source

    def next(self):
        #TODO: Actual lexing

