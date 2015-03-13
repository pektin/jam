class CompilerError(Exception):
    def __init__(self, err, tokens = []):
        super().__init__(err)
        self.tokens = tokens

    def format(self, source:str):
        lines = {}

        for token in self.tokens:
            for pos in range(token.start, token.end):
                number, line, pos = self._getLine(pos, source)
                if number not in lines:
                    lines[number] = [line, " " * len(line)]

                lines[number][1] = lines[number][1][:pos - 1] + "^" + lines[number][1][pos:]

        out = "\n"

        for number, line in lines.items():
            line_number = str(number)
            out += line_number + "| " + line[0]
            out += len(line_number) * " " + "| " + line[1] + "\n"

        self.args = (self.args[0] + out,)

    def _getLine(self, pos:int, source:str):
        number = 1
        line = ""

        for index, char in enumerate(source):
            if index >= pos:
                line += char

                if char == "\n":
                    break
            elif char == "\n":
                number += 1

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
