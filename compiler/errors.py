# A singular message for an error. An error is made up of multiple error messages
# A error message defines the formatting of an error.
class _ErrorMessage:
    def __init__(self, message:str = None,
                       content:str = None,
                       object = None,
                       tokens:[] = None,
                       source = None):
        # Grab message, tokens and source from object if empty
        if object is not None:
            if message is None:
                message = "`{}`".format(object)
            if tokens is None:
                tokens = object.tokens
            if source is None:
                source = object.source
        # Put quoted message if content
        if content is not None:
            message = "`{}`".format(content)

        self.message = message
        self.tokens = tokens
        self.source = source

    # Return a 3-tuple of the line number, start and end position of the line
    # at position in source
    def _getLine(self, source:str, position:int):
        number = source[:position].count("\n") + 1
        start = position - len(source[:position].rpartition("\n")[2])
        end = position + len(source[position:].partition("\n")[0]) + 1
        return number, start, end

    def format(self):
        if self.source is None or self.tokens is None:
            return self.message, None

        # Read in entire source (could be optimised)
        self.source.seek(0)
        source = self.source.read()

        lines = {}
        for token in self.tokens:
            number, start, end = self._getLine(source, token.start)
            line = lines.setdefault(number, (set(), start, end))
            line[0].update(set(range(token.start, token.end)))

        appendix = []
        for number, (highlights, start, end) in sorted(lines.items(), key=lambda a: a[0]):
            number_str = str(number)
            appendix.append("{}| {}{}| {}".format(
                number_str,
                source[start:end],
                " " * len(number_str),
                "".join(("^" if i in highlights else " ") for i in range(start, end))
            ))

        return self.message, "\n".join(appendix)

# Generic CompilerError
class CompilerError(Exception):
    # Create a new CompilerError
    #
    # A compiler error takes a single error message and a list of tokens.
    # When displayed, the error will contain the specified message along with
    # nicely formatted source code extracts, highlighting the specified tokens
    def __init__(self, **kwargs):
        Exception.__init__(self, "")
        self.messages = []
        self.notes = []
        self.add(**kwargs)

    def add(self, **kwargs):
        self.messages.append(_ErrorMessage(**kwargs))
        return self

    def addNote(self, **kwargs):
        self.notes.append(_ErrorMessage(**kwargs))
        return self

    def _format(self, list):
        content = []
        appendix = []

        for message in list:
            message = message.format()
            if message[0]: content.append(message[0])
            if message[1]: appendix.append(message[1])

        return " ".join(content) + "\n" + "\n".join(appendix)

    def format(self):
        self.args = (self._format(self.messages) + self._format(self.notes),)

class SyntaxError(CompilerError):
    pass

class SemanticError(CompilerError):
    pass

class TypeError(SemanticError):
    pass

class DependencyError(TypeError):
    pass

class ValueError(SemanticError):
    pass

class AmbiguityError(SemanticError):
    pass

class MissingReferenceError(SemanticError):
    pass

class ImportError(SemanticError):
    pass

class ExecutionError(Exception):
    pass

class InternalError(Exception):
    pass

from . import lekvar
