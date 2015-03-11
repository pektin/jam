from io import IOBase

from .. errors import *
from ..lekvar import lekvar
from .lexer import Lexer, Tokens

#
# Setup functions
#

def parseFile(source:IOBase):
    return Parser(Lexer(source)).parseModule()

class Parser:
    lexer = None
    tokens = None

    def __init__(self, lexer):
        self.lexer = lexer
        self.tokens = []

    def next(self):
        if len(self.tokens) == 0:
            return self.lexer.lex()
        else:
            return self.tokens.pop(0)

    def lookAhead(self, num = 1):
        while len(self.tokens) < num:
            self.tokens.append(self.lexer.lex())
        return self.tokens[num - 1]

    def _unexpected(self, token):
        raise SyntaxError("Unexpected {}: '{}'".format(token.type, token.data))

    def strip(self, types:[Tokens] = [Tokens.newline]):
        # Strip all tokens of a type, returning one lookAhead or None
        token = self.lookAhead()
        while token.type in types:
            self.next()
            token = self.lookAhead()
            if token is None: return None
        return token

    def expect(self, type:Tokens = Tokens.identifier):
        # Parse for an expected token, returning it's data
        token = self.next()
        if token.type != type:
            self._unexpected(token)
        return token.data

    def parseModule(self):
        children = {}
        instructions = []

        while True:
            value = self.parseLine()

            # EOF escape
            if value is None: break

            if isinstance(value, lekvar.ScopeObject):
                # Scopes are automatically added as children
                name = value.name

                if isinstance(value, lekvar.Method):

                    if name in children:
                        children[name].assimilate(value)
                    else:
                        children[name] = value
                else:
                    children[name] = value
            else:
                # Other values are added as instructions
                instructions.append(value)

        return lekvar.Module("main", list(children.values()),
               lekvar.Function("main", [], instructions, None))

    def parseLine(self):
        # Parse a line. The line may not exist

        # Ignore newlines
        token = self.strip()
        if token is None: return None

        if token.type == Tokens.comment:
            return lekvar.Comment(self.next().data)
        elif token.type == Tokens.keyword:
            if token.data == "return":
                return self.parseReturn()
        elif token.type == Tokens.identifier:
            if self.lookAhead(2).type == Tokens.equal:
                return self.parseAssignment()
        return self.parseValue()

    def parseValue(self):
        value = self.parseSingleValue()

        token = self.lookAhead()

        if token.type == Tokens.group_start:
            return self.parseCall(value)
        elif token.type == Tokens.dot:
            return self.parseAttribute(value)
        else:
            return value

    def parseSingleValue(self):
        # Parse for a value. The value is expected to exist

        token = self.lookAhead()

        # Ignore comments and newlines until a value is reached
        token = self.strip([Tokens.comment, Tokens.newline])
        # EOF handling
        if token is None:
            raise SyntaxError("Expected value before EOF")

        # Identify the kind of value
        if token.type == Tokens.keyword:
            if token.data == "def":
                return self.parseMethod()
            elif token.data == "class":
                return self.parseClass()
        elif token.type == Tokens.identifier:
            return lekvar.Reference(self.next().data)
        elif token.type == Tokens.string:
            token = self.next()
            return lekvar.Literal(token.data, lekvar.Reference("String"))

        self._unexpected(token)

    def parseMethod(self):
        # "def" should have already been identified
        self.next()

        name = self.expect()

        arguments = []
        default_values = []

        token = self.lookAhead()
        if token.type != Tokens.newline and token.type != Tokens.typeof: # Allow for no arguments
            token = self.next()

            # Arguments start with "("
            if token.type != Tokens.group_start:
                self._unexpected(token)

            if self.lookAhead().type != Tokens.group_end: # Allow for no arguments

                # Parse arguments
                while True:
                    arguments.append(self.parseVariable())

                    # Parse default arguments
                    token = self.next()
                    if token.type == Tokens.equal:
                        default_values.append(self.parseValue())
                        token = self.next()
                    else:
                        default_values.append(None)

                    # Arguments separated by comma
                    if token.type == Tokens.comma:
                        continue
                    # Arguments end with ")"
                    elif token.type == Tokens.group_end:
                        break
                    else:
                        self._unexpected(token)
            else:
                self.next()

        return_type = self.parseTypeSig()


        # Parse instructions
        instructions = []

        while True:
            token = self.strip()

            if token is None:
                raise SyntaxError("Expected 'end' before EOF")

            if token.type == Tokens.keyword:
                if token.data == "end":
                    self.next()
                    break
            instructions.append(self.parseLine())

        # Create method with default arguments
        overloads = [lekvar.Function("", arguments, instructions, return_type)]

        in_defaults = True
        for index, value in enumerate(reversed(default_values)):
            index = -index - 1
            if in_defaults:
                if value is None:
                    in_defaults = False
                else:
                    # Copy arguments
                    args = [arg.copy() for arg in arguments[:index]]

                    # Add an overload calling the previous overload with the default argument
                    overloads.append(
                        lekvar.Function("", args, [
                            lekvar.Call(
                                overloads[-1],
                                # Add non-default arguments with the default value
                                args + [default_values[index]],
                            )
                        ])
                    )
            else:
                # Check for default arguments before a non-defaulted argument
                if value is not None:
                    raise SyntaxError("Cannot have non-defaulted arguments after defaulted ones")

        return lekvar.Method(name, overloads)

    def parseClass(self):
        # class should have already been identified
        token = self.next()

        name = self.expect()

        attributes = []

        while True:
            token = self.strip()
            if token is None:
                raise SyntaxError("Expected 'end' before EOF")
            elif token.type == Tokens.keyword:
                if token.data == "end":
                    self.next()
                    break
                elif token.data == "def":
                    attributes.append(self.parseMethod())
            elif token.type == Tokens.identifier:
                attributes.append(self.parseVariable())
            else:
                self._unexpected(token)

        return lekvar.Class(name, attributes)


    def parseVariable(self):
        # Parse a variable, with optional type signature

        name = self.expect()
        type = self.parseTypeSig()

        return lekvar.Variable(name, type)

    def parseTypeSig(self):
        # Parse an optional type signature
        if self.lookAhead().type != Tokens.typeof:
            return None
        self.next()

        return self.parseType()

    def parseType(self):
        # Parse an expected type

        name = self.expect()
        return lekvar.Reference(name)

    def parseCall(self, called):
        # Parse a function call

        assert self.next().type == Tokens.group_start

        arguments = []
        if self.lookAhead().type != Tokens.group_end:

            # Parse arguments
            while True:
                arguments.append(self.parseValue())

                token = self.next()
                if token.type == Tokens.comma:
                    continue
                elif token.type == Tokens.group_end:
                    break
                else:
                    self._unexpected(token)
        else:
            self.next()

        return lekvar.Call(called, arguments)

    def parseReturn(self):
        # Parse a return statement

        # return keyword is expected to be parsed
        self.next()

        if self.lookAhead().type != Tokens.newline:
            value = self.parseValue()
        else:
            value = None

        return lekvar.Return(value)

    def parseAssignment(self):
        # Parse a assignment

        variable = self.parseVariable()

        assert self.next().type == Tokens.equal

        value = self.parseValue()
        return lekvar.Assignment(variable, value)

    def parseAttribute(self, value):
        assert self.next().type == Tokens.dot

        attribute = self.expect()
        return lekvar.Attribute(value, attribute)
