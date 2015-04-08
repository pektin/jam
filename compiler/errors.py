# Generic CompilerError
class CompilerError(Exception):
    # Create a new CompilerError
    #
    # A compiler error takes a single error message and a list of tokens.
    # When displayed, the error will contain the specified message along with
    # nicely formatted source code extracts, highlighting the specified tokens
    def __init__(self, err, tokens = []):
        super().__init__(err)
        self.tokens = tokens

    # Formats the error message given a specified source
    #
    # This is presented as a separate function because the error may be
    # caught multiple times, each adding in related tokens. This allows for more
    # robust error handling while avoiding massive overhead.
    #
    # Compiler errors are designed to be caught by the compiler and formatted
    # before being returned to the rest of the program
    def format(self, source:str):

        # Collect a set of line numbers linked to the contents of that line
        # and the highlighting of specified tokens on that line
        lines = {}
        for token in self.tokens:
            # Loop through each character position of the token
            # This might need some optimisation
            for pos in range(token.start, token.end):
                number, line, pos = self._getLine(pos, source)

                # Produce new 'lines' entries
                if number not in lines:
                    lines[number] = [line, " " * len(line)]

                # Highlight the character
                lines[number][1] = lines[number][1][:pos - 1] + "^" + lines[number][1][pos:]

        # Produce the final error message
        out = "\n"

        # Start each source reference with the line number, to match the
        # behaviour of text editors
        for number, line in lines.items():
            line_number = str(number)
            out += line_number + "| " + line[0]
            out += len(line_number) * " " + "| " + line[1] + "\n"

        # Set the exceptions error message
        self.args = (self.args[0] + out,)

    # Given the source code and the position of a character, this function
    # returns the line number, the line itself and the relative position of the
    # character in the line that the character is contained in.
    def _getLine(self, pos:int, source:str):
        number = 1
        line = ""

        # Iterate until the character is reached, counting the number of lines
        # cache each new line encountered
        for index, char in enumerate(source):
            if index >= pos:
                line += char

                if char == "\n":
                    break
            elif char == "\n":
                number += 1

        # Continue from the cached line for the rest of the line the character is in
        index = pos - 1
        while index >= 0:
            if source[index] == "\n":
                break

            line = source[index] + line
            index -= 1

        return number, line, pos - index


class SyntaxError(CompilerError):
    pass

class SemanticError(CompilerError):
    pass

class TypeError(SemanticError):
    pass

class ValueError(SemanticError):
    pass

class AmbiguetyError(SemanticError):
    pass

class MissingReferenceError(SemanticError):
    pass

class InternalError(CompilerError):
    pass
