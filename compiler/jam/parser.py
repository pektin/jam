import logging
from io import IOBase

from .. errors import *
from .. import lekvar
from .lexer import Lexer, Tokens

#
# Tools
#

def parseFile(source:IOBase, logger=logging.getLogger()):
    return Parser(Lexer(source), logger).parseModule(False)

#
# Parser
#

BINARY_OPERATIONS = [
    {Tokens.equality, Tokens.inequality,
     Tokens.smaller_than, Tokens.smaller_than_or_equal_to,
     Tokens.greater_than, Tokens.greater_than_or_equal_to},
    {Tokens.addition, Tokens.subtraction},
    {Tokens.multiplication, Tokens.division, Tokens.integer_division},
]

OPERATION_TOKENS = {type for operation in BINARY_OPERATIONS for type in operation }

class Parser:
    lexer = None
    tokens = None
    logger = None

    def __init__(self, lexer, logger):
        self.lexer = lexer
        self.tokens = []
        self.logger = logger.getChild("Parser")

    # Return the next token and move forward by one token
    def next(self):
        if len(self.tokens) == 0:
            return self.lexer.lex()
        else:
            return self.tokens.pop(0)

    # Look ahead of the current token by num tokens
    def lookAhead(self, num = 1):
        while len(self.tokens) < num:
            self.tokens.append(self.lexer.lex())
        return self.tokens[num - 1]

    # Throw an unexpected token error
    def _unexpected(self, token):
        raise SyntaxError("Unexpected {}: '{}'".format(token.type, token.data), [token])

    # Strip all tokens of a type, returning one lookAhead or None
    def strip(self, types:[Tokens] = [Tokens.newline]):
        token = self.lookAhead()
        if token is None: return None

        while token.type in types:
            self.next()
            token = self.lookAhead()
            if token is None: return None

        return token

    # Parse for an expected token, returning it's data
    def expect(self, type:Tokens):
        token = self.next()
        if token.type != type:
            self._unexpected(token)
        return token

    def parseModule(self, inline = True):

        if inline:
            tokens = [self.next()]
            assert tokens[0].type == Tokens.module_kwd

            tokens.append(self.expect(Tokens.identifier))
            module_name = tokens[1].data
        else:
            tokens = None
            module_name = "main"

        children = {}
        instructions = []

        while True:
            # Check for end_kwd
            if inline:
                token = self.strip()
                if token is None:
                    raise SyntaxError("Expected 'end' before EOF")
                elif token.type == Tokens.end_kwd:
                    tokens.append(self.next())
                    break

            value = self.parseLine()

            # EOF escape
            if value is None: break

            if isinstance(value, lekvar.BoundObject):
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

        return lekvar.Module(module_name, list(children.values()),
               lekvar.Function("", [], instructions, None, static=True), tokens)

    def parseLine(self):
        # Parse a line. The line may not exist

        # Ignore newlines
        token = self.strip()
        if token is None: return None

        if token.type == Tokens.comment:
            return self.parseComment()
        elif token.type == Tokens.return_kwd:
            return self.parseReturn()
        elif token.type == Tokens.identifier:
            if self.lookAhead(2).type == Tokens.equal:
                return self.parseAssignment()
        elif token.type == Tokens.if_kwd:
            return self.parseBranch()
        elif token.type == Tokens.while_kwd:
            return self.parseWhile()
        elif token.type == Tokens.loop_kwd:
            return self.parseLoop()
        elif token.type == Tokens.break_kwd:
            return self.parseBreak()
        return self.parseValue()

    def parseValue(self):
        values = [self.parseUnaryOperation()]
        operations = []

        while True:
            token = self.strip([Tokens.comment, Tokens.newline])

            if token and token.type in OPERATION_TOKENS:
                operations.append(self.next())
                values.append(self.parseUnaryOperation())
            else:
                break

        return self.parseBinaryOperation(values, operations)

    def parseBinaryOperation(self, values, operations, operation_index = 0):
        if len(values) == 1:
            return values[0]

        if operation_index == len(BINARY_OPERATIONS):
            raise InternalError("Unparsed operations detected {}".format(values))


        # Accumulate values from higher order operations
        # Separated by current order operations
        operation_values = []
        operation_operations = []

        previous_index = 0
        for index, operation in enumerate(operations):
            if operation.type in BINARY_OPERATIONS[operation_index]:
                operation_operations.append(operation)

                operation_values.append(self.parseBinaryOperation(
                    values[previous_index:index + 1],
                    operations[previous_index:index],
                    operation_index + 1,
                ))
                previous_index = index + 1
        operation_values.append(self.parseBinaryOperation(
            values[previous_index:],
            operations[previous_index:],
            operation_index + 1,
        ))

        # Accumulate operations (left to right)
        lhs = operation_values[0]
        for index, operation in enumerate(operation_operations):
            rhs = operation_values[index + 1]
            lhs = lekvar.Call(lekvar.Attribute(lhs, operation.data), [rhs], operation)

        return lhs

    def parseUnaryOperation(self):
        value = self.parseSingleValue()

        while True:
            token = self.strip([Tokens.comment, Tokens.newline])

            if token is None:
                break

            if token.type == Tokens.group_start:
                value = self.parseCall(value)
            elif token.type == Tokens.dot:
                value = self.parseAttribute(value)
            else:
                break

        return value

    def parseSingleValue(self):
        # Ignore comments and newlines until a value is reached
        token = self.strip([Tokens.comment, Tokens.newline])

        # EOF handling
        if token is None:
            raise SyntaxError("Expected value before EOF")

        # Identify the kind of value
        if token.type == Tokens.def_kwd:
            return self.parseMethod()
        elif token.type == Tokens.class_kwd:
            return self.parseClass()
        elif token.type == Tokens.module_kwd:
            return self.parseModule()
        elif token.type == Tokens.identifier:
            return lekvar.Reference(self.next().data)
        elif token.type in (Tokens.integer, Tokens.dot):
            return self.parseNumber()
        elif token.type in (Tokens.true_kwd, Tokens.false_kwd):
            return self.parseConstant()
        elif token.type == Tokens.string:
            token = self.next()
            return lekvar.Literal(token.data, lekvar.Reference("String"))
        elif token.type == Tokens.group_start:
            return self.parseGrouping()

        self._unexpected(token)

    def parseGrouping(self):
        token = self.next()
        assert token.type == Tokens.group_start

        value = self.parseValue()

        self.expect(Tokens.group_end)

        return value

    def parseConstant(self):
        token = self.next()

        if token.type == Tokens.true_kwd:
            return lekvar.Literal(True, lekvar.Reference("Bool"))
        elif token.type == Tokens.false_kwd:
            return lekvar.Literal(False, lekvar.Reference("Bool"))
        else:
            raise InternalError("Invalid constant token type")

    def parseComment(self):
        token = self.next()
        assert token.type == Tokens.comment
        return lekvar.Comment(token.data, [token])

    def parseNumber(self):
        tokens = [self.next()]

        # Float starting with a dot
        if tokens[0].type == Tokens.dot:

            token = self.next()
            if token.type != Tokens.integer:
                self._unexpected(token)

            tokens.append(token)
            value = float("." + token.data.replace("_", ""))
            return lekvar.Literal(value, lekvar.Reference("Real"), tokens)

        assert tokens[0].type == Tokens.integer

        token = self.lookAhead()

        # Float with dot in the middle
        if token.type == Tokens.dot:
            tokens.append(self.next())

            value = float(tokens[0].data.replace("_", "") + ".")

            token = self.next()
            tokens.append(token)

            if token.type == Tokens.integer:
                value += float("." + token.data.replace("_", ""))
            else:
                self._unexpected(token)

            return lekvar.Literal(value, lekvar.Reference("Real"), tokens)

        # Integer
        else:
            value = int(tokens[0].data.replace("_", ""))
            return lekvar.Literal(value, lekvar.Reference("Int"), tokens)

    def parseMethod(self):
        # starting keyword should have already been identified
        tokens = [self.next()]
        assert tokens[0].type == Tokens.def_kwd

        # Parse different kinds of methods

        # Operations
        if self.lookAhead().type == Tokens.self_kwd:
            tokens.append(self.next())

            token = self.next()
            if token.type not in OPERATION_TOKENS:
                raise SyntaxError("{} is not a valid operation".format(token), [token])
            name = token.data

            tokens.append(token)

            arguments = [self.parseVariable()]
            default_values = [None]
        # Normal named methods
        else:
            token = self.expect(Tokens.identifier)
            tokens.append(token)
            name = token.data
            arguments, default_values = self.parseMethodArguments()

        return_type = self.parseTypeSig(Tokens.returns)

        return self.parseMethodBody(name, arguments, default_values, return_type, tokens)

    def parseConstructor(self):
        # starting keyword should have already been identified
        tokens = [self.next()]
        assert tokens[0].type == Tokens.new_kwd

        name = ""
        arguments, default_values = self.parseMethodArguments()

        return self.parseMethodBody(name, arguments, default_values, None, tokens)

    def parseMethodBody(self, name, arguments, default_values, return_type, tokens):
        # Parse instructions
        instructions = []

        while True:
            token = self.strip()

            if token is None:
                raise SyntaxError("Expected 'end' before EOF")

            if token.type == Tokens.end_kwd:
                tokens.append(self.next())
                break
            instructions.append(self.parseLine())

        # Create method with default arguments
        overloads = [lekvar.Function("", arguments, instructions, return_type, tokens)]

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
                        ], return_type, tokens)
                    )
            else:
                # Check for default arguments before a non-defaulted argument
                if value is not None:
                    raise SyntaxError("Cannot have non-defaulted arguments after defaulted ones")

        return lekvar.Method(name, overloads)

    def parseMethodArguments(self):
        arguments, default_values = [], []

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

        return arguments, default_values

    def parseClass(self):
        # class should have already been identified
        assert self.next().type == Tokens.class_kwd

        name = self.expect(Tokens.identifier).data

        constructor = None
        attributes = []

        while True:
            token = self.strip()
            if token is None:
                raise SyntaxError("Expected 'end' before EOF")
            elif token.type == Tokens.end_kwd:
                self.next()
                break
            elif token.type == Tokens.def_kwd:
                meth = self.parseMethod()
                attributes.append(meth)
            elif token.type == Tokens.new_kwd:
                meth = self.parseConstructor()
                constructor = meth
            elif token.type == Tokens.identifier:
                attributes.append(self.parseVariable())
            else:
                self._unexpected(token)

        return lekvar.Class(name, constructor, attributes)

    def parseWhile(self):
        tokens = [self.next()]

        assert tokens[0].type == Tokens.while_kwd

        condition = self.parseValue()

        instructions = []

        while True:
            token = self.strip()

            if token is None:
                raise SyntaxError("Expected 'end' before EOF")

            elif token.type == Tokens.end_kwd:
                tokens.append(self.next())
                break

            instructions.append(self.parseLine())

        branch = lekvar.Branch(condition, [], [lekvar.Break()])
        return lekvar.Loop([branch] + instructions, tokens)

    def parseLoop(self):
        tokens = [self.next()]

        assert tokens[0].type == Tokens.loop_kwd

        instructions = []

        while True:
            token = self.strip()

            if token is None:
                raise SyntaxError("Expected 'end' before EOF")

            elif token.type == Tokens.end_kwd:
                tokens.append(self.next())
                break

            instructions.append(self.parseLine())

        return lekvar.Loop(instructions, tokens)

    def parseBreak(self):
        token = self.next()

        assert token.type == Tokens.break_kwd

        return lekvar.Break([token])

    def parseBranch(self):
        tokens = [self.next()]

        assert tokens[0].type == Tokens.if_kwd

        condition = self.parseValue()

        if_instructions = []

        while True:
            token = self.strip()

            if token is None:
                raise SyntaxError("Expected 'end' or 'else' before EOF")

            elif token.type == Tokens.end_kwd:
                tokens.append(self.next())
                return lekvar.Branch(condition, if_instructions, [], tokens)

            elif token.type == Tokens.else_kwd:
                tokens.append(self.next())
                break

            if_instructions.append(self.parseLine())

        else_instructions = []

        while True:
            token = self.strip()

            if token is None:
                raise SyntaxError("Expected 'end' before EOF")

            elif token.type == Tokens.end_kwd:
                tokens.append(self.next())
                return lekvar.Branch(condition, if_instructions, else_instructions, tokens)

            else_instructions.append(self.parseLine())

    # Parse a variable, with optional type signature
    def parseVariable(self):
        tokens = [self.expect(Tokens.identifier)]
        name = tokens[0].data
        type = self.parseTypeSig()

        return lekvar.Variable(name, type, tokens)

    # Parse an optional type signature
    def parseTypeSig(self, typeof = Tokens.typeof):
        if self.lookAhead().type != typeof:
            return None
        self.next()

        return self.parseValue()

    # Parse a function call
    def parseCall(self, called):
        tokens = [self.next()]
        assert tokens[0].type == Tokens.group_start

        arguments = []
        if self.lookAhead().type != Tokens.group_end:

            # Parse arguments
            while True:
                arguments.append(self.parseValue())

                token = self.next()
                if token.type == Tokens.comma:
                    continue
                elif token.type == Tokens.group_end:
                    tokens.append(token)
                    break
                else:
                    self._unexpected(token)
        else:
            self.next()

        return lekvar.Call(called, arguments, tokens)

    # Parse a return statement
    def parseReturn(self):
        # return keyword is expected to be parsed
        tokens = [self.next()]
        assert tokens[0].type == Tokens.return_kwd

        if self.lookAhead().type != Tokens.newline:
            value = self.parseValue()
        else:
            value = None

        return lekvar.Return(value, tokens)

    # Parse a assignment
    def parseAssignment(self):
        variable = self.parseVariable()

        tokens = [self.next()]
        assert tokens[0].type == Tokens.equal

        value = self.parseValue()
        return lekvar.Assignment(variable, value, tokens)

    def parseAttribute(self, value):
        tokens = [self.next()]
        assert tokens[0].type == Tokens.dot

        attribute = self.expect(Tokens.identifier).data
        return lekvar.Attribute(value, attribute, tokens)
