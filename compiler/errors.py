class _Token:
    start = 0
    end = 0

def formatTokens(source:str, tokens:[_Token]):
    # a mapping of line numbers to a line and set of positions in that line
    lines = {}

    for token in tokens:
        line = _getLine(source, token.start)

        if line.number not in lines:
            lines[line.number] = (line, set())

        for position in range(token.start, token.end):
            lines[line.number][1].add(position)

    out = []

    for number, (line, highlights) in sorted(lines.items(), key=lambda a: a[0]):
        number_str = str(number)
        out.append("{}| {}{}| {}".format(
            number_str,
            source[line.start:line.end],
            " " * len(number_str),
            "".join(("^" if index in highlights else " ")
                for index in range(line.start, line.end))
        ))

    return "\n".join(out)

def _getLine(source:str, position:int):
    class Line:
        def __init__(self, number):
            self.number = number
            self.start = 0
            self.end = 0

    line = Line(1)

    # Get the line number and starting index of said line at the position
    for index, character in enumerate(source):
        if index == position:
            break
        elif character == "\n":
            line.number += 1
            line.position = index + 1

    # Get the end index of the line
    line.end = line.start
    for index, character in enumerate(source[line.start:]):
        line.end += 1
        if character == "\n": # Include the newline
            break

    return line

# Generic CompilerError
class CompilerError(Exception):
    # Create a new CompilerError
    #
    # A compiler error takes a single error message and a list of tokens.
    # When displayed, the error will contain the specified message along with
    # nicely formatted source code extracts, highlighting the specified tokens
    def __init__(self, message:str, tokens:[_Token] = None):
        super().__init__("")
        self.messages = []
        if isinstance(message, list):
            for msg in message:
                self.addMessage(*msg)
        else:
            self.addMessage(message, tokens)

    def addMessage(self, message:str, tokens:[_Token]):
        if message or tokens:
            self.messages.append((message, tokens))

    def format(self, source:str):
        message = "\n".join(
            (msg if msg else "") +
            ("\n" if msg and tokens else "") +
            (formatTokens(source, tokens) if tokens else "")
                for msg, tokens in self.messages
        )
        self.args = (message,)

class SyntaxError(CompilerError):
    pass

class SemanticError(CompilerError):
    pass

class TypeError(SemanticError):
    pass

class ValueError(SemanticError):
    pass

class AmbiguityError(SemanticError):
    pass

class MissingReferenceError(SemanticError):
    pass

class InternalError(Exception):
    pass
