import logging
from io import IOBase

from .. errors import *
from .. import lekvar

from .lexer import Lexer, Tokens

#
# Tools
#

def parseFile(source:IOBase, logger=logging.getLogger()):
    with lekvar.State.ioSource(source):
        try:
            module = Parser(Lexer(source), logger).parseModule(False)
            if hasattr(source, "name"): module.name = source.name
            return module
        except CompilerError as e:
            source.seek(0)
            e.format()
            raise e

#
# Parser
#

BINARY_OPERATIONS = [
    {Tokens.assign},
    {Tokens.logical_and},
    {Tokens.logical_or},
    {Tokens.equality, Tokens.inequality,
     Tokens.smaller_than, Tokens.smaller_than_or_equal_to,
     Tokens.greater_than, Tokens.greater_than_or_equal_to},
    {Tokens.addition, Tokens.subtraction},
    {Tokens.multiplication, Tokens.division, Tokens.integer_division, Tokens.mod},
]

BINARY_OPERATION_TOKENS = { type for operation in BINARY_OPERATIONS for type in operation }

BINARY_OPERATION_FUNCTIONS = {
    Tokens.logical_and: "&&",
    Tokens.logical_or: "||",
}

UNARY_OPERATIONS = [
    Tokens.addition,
    Tokens.subtraction,
    Tokens.logical_negation,
]

UNARY_OPERATION_TOKENS = set(UNARY_OPERATIONS)

class Parser:
    lexer = None
    tokens = None
    logger = None

    def __init__(self, lexer, logger):
        self.lexer = lexer
        self.tokens = []
        self.logger = logger.getChild("Parser")

    @property
    def source(self): return self.lexer.source

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
        raise SyntaxError(message="Unexpected").add(content=token.data, tokens=[token], source=self.source)

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
    # May also pass a tokens argument, to which the lexed token is appended
    def expect(self, type:Tokens, tokens:[] = None):
        token = self.next()

        if token is None:
            raise SyntaxError(message="Expected").add(content=type.name).add(message="before EOF")

        if token.type != type:
            self._unexpected(token)

        if tokens is not None:
            tokens.append(token)

        return token

    def parseInstructionOrChild(self, instructions:[lekvar.Object], children:{str: lekvar.BoundObject}):
        value = self.parseLine()
        if value is None: return None

        if isinstance(value, lekvar.BoundObject):
            self.addChild(children, value)
        else:
            instructions.append(value)

        return value

    def addChild(self, children:{str: lekvar.BoundObject}, value:lekvar.BoundObject):
        name = value.name

        if isinstance(value, lekvar.Method):
            if name in children:
                children[name].assimilate(value)
            else:
                children[name] = value
        else:
            children[name] = value

    def parseModule(self, inline = True):
        tokens = []

        if inline:
            self.expect(Tokens.module_kwd, tokens)

            module_name = self.expect(Tokens.identifier, tokens).data
        else:
            module_name = "main"

        self.expect(Tokens.newline, tokens)

        children = {}
        instructions = []

        while True:
            # Check for end_kwd
            if inline:
                token = self.lookAhead()
                if token is None:
                    raise SyntaxError(message="Expected").add(content="end").add(message="before EOF").addNote(tokens=tokens, source=self.source)
                elif token.type == Tokens.end_kwd:
                    tokens.append(self.next())
                    break

            if self.parseInstructionOrChild(instructions, children) is None:
                break

        return lekvar.Module(module_name, list(children.values()), instructions, tokens)

    def parseLine(self):
        # Parse a line. The line may not exist

        token = self.strip()
        if token is None: return None

        if token.type == Tokens.return_kwd:
            value = self.parseReturn()
        elif token.type == Tokens.import_kwd:
            value = self.parseImport()
        elif token.type == Tokens.if_kwd:
            value = self.parseBranch()
        elif token.type == Tokens.while_kwd:
            value = self.parseWhile()
        elif token.type == Tokens.loop_kwd:
            value = self.parseLoop()
        elif token.type == Tokens.break_kwd:
            value = self.parseBreak()
        else:
            value = self.parseValue()
        self.expect(Tokens.newline)
        return value

    def parseValue(self):
        values = [self.parseUnaryOperation()]
        operations = []

        while True:
            token = self.lookAhead()

            if token and token.type in BINARY_OPERATION_TOKENS:
                operations.append(self.next())
                values.append(self.parseUnaryOperation())
            else:
                break

        return self.parseBinaryOperation(values, operations)

    def parseBinaryOperation(self, values, operations, operation_index = 0):
        if len(values) == 1:
            return values[0]

        if operation_index == len(BINARY_OPERATIONS):
            raise InternalError("Unparsed operation {}".format(values))

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

            # The assignment operation is special
            if operation.type == Tokens.assign:
                lhs = lekvar.Assignment(lhs, rhs, [operation])
                continue

            # Some operations are attributes of the lhs, others are global functions
            if operation.type in BINARY_OPERATION_FUNCTIONS:
                lhs = lekvar.Operation(lekvar.Reference(BINARY_OPERATION_FUNCTIONS[operation.type]), [lhs, rhs], None, [operation])
            else:
                lhs = lekvar.Operation(lekvar.Attribute(lhs, operation.data), [rhs], None, [operation])

        return lhs

    def parseUnaryOperation(self):
        # Collect prefix unary operations
        operations = []
        while True:
            token = self.lookAhead()

            if token is None:
                break

            if token.type in UNARY_OPERATION_TOKENS:
                operations.insert(0, self.next())
            else:
                break

        value = self.parseSingleValue()

        # Make prefix operations
        for operation in operations:
            value = lekvar.Call(lekvar.Attribute(value, operation.data), [], None, [operation])

        # Postfix unary operations
        while True:
            token = self.lookAhead()

            if token is None:
                break

            if token.type == Tokens.group_start:
                value = self.parseCall(value)
            elif token.type == Tokens.dot:
                value = self.parseAttribute(value)
            elif token.type == Tokens.as_kwd:
                value = self.parseCast(value)
            else:
                break

        return value

    def parseSingleValue(self):
        # Ignore comments and newlines until a value is reached
        token = self.lookAhead()

        # EOF handling
        if token is None:
            raise SyntaxError(message="Expected value before EOF") #TODO: Add token reference

        # Identify the kind of value
        if token.type == Tokens.def_kwd:
            return self.parseMethod()
        elif token.type == Tokens.class_kwd:
            return self.parseClass()
        elif token.type == Tokens.module_kwd:
            return self.parseModule()
        elif token.type == Tokens.identifier:
            return lekvar.Reference(token.data, [self.next()])
        elif token.type in (Tokens.integer, Tokens.dot):
            return self.parseNumber()
        elif token.type in (Tokens.true_kwd, Tokens.false_kwd):
            return self.parseConstant()
        elif token.type == Tokens.string:
            token = self.next()
            return lekvar.Literal(token.data, lekvar.Reference("String"), [token])
        elif token.type == Tokens.format_string:
            token = self.next()
            return lekvar.Literal(token.data.encode("UTF-8").decode("unicode-escape"),
                lekvar.Reference("String"), [token])
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
        if token is not None and token.type == Tokens.dot:
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

        # Non cast operations
        if self.lookAhead(2).type not in [Tokens.as_kwd, Tokens.typeof]:
            # Operations with self on lhs
            if self.lookAhead().type == Tokens.self_kwd:
                tokens.append(self.next())

                token = self.lookAhead()
                # Binary Operations
                if token.type in BINARY_OPERATION_TOKENS:
                    name = token.data
                    tokens.append(self.next())

                    arguments = [self.parseVariable()]
                    default_values = [None]
                # Call Operation
                elif token.type == Tokens.group_start:
                    name = ""
                    arguments, default_values = self.parseMethodArguments()
                else:
                    raise SyntaxError(content=token.data, tokens=[token], source=self.source).add(message="is not a valid operation")
            # Prefix Unary Operations
            elif self.lookAhead(2).type == Tokens.self_kwd:
                token = self.next()
                if token.type not in UNARY_OPERATION_TOKENS:
                    raise SyntaxError(content=token.data, tokens=[token], source=self.source).add(message="is not a valid operation")
                name = token.data

                tokens.append(token)
                tokens.append(self.next())

                arguments = []
                default_values = []
            # Normal named methods
            else:
                name = self.expect(Tokens.identifier, tokens).data
                arguments, default_values = self.parseMethodArguments()

            return_type = self.parseTypeSig(Tokens.returns)

        # Cast operations
        else:
            self.expect(Tokens.self_kwd, tokens)

            # Explicit casts
            if self.lookAhead().type == Tokens.as_kwd:
                tokens.append(self.next())

                name = "as"

                arguments = []
                default_values = []
            # Implicit casts
            else:
                #TODO
                raise InternalError()

            return_type = self.parseSingleValue()

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
        children = {}

        while True:
            token = self.strip()

            if token is None:
                raise SyntaxError(message="Expected `end` before EOF").add(tokens=tokens, source=self.source)

            if token.type == Tokens.end_kwd:
                tokens.append(self.next())
                break
            self.parseInstructionOrChild(instructions, children)

        # Create method with default arguments
        overloads = [lekvar.Function("", arguments, instructions, list(children.values()), return_type, tokens)]

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
                        ], list(children.values()), return_type, tokens)
                    )
            else:
                # Check for default arguments before a non-defaulted argument
                if value is not None:
                    raise SemanticError(message="Cannot have non-defaulted arguments after defaulted ones").add(message="", object=value)

        return lekvar.Method(name, overloads)

    def parseMethodArguments(self):
        arguments, default_values = [], []

        # Arguments start with "("
        self.expect(Tokens.group_start)

        if self.lookAhead().type != Tokens.group_end: # Allow for no arguments
            # Parse arguments
            while True:
                arguments.append(self.parseVariable())

                # Parse default arguments
                token = self.next()
                if token.type == Tokens.assign:
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
        tokens = [self.next()]
        assert tokens[0].type == Tokens.class_kwd

        name = self.expect(Tokens.identifier, tokens).data

        constructor = None
        attributes = {}

        while True:
            token = self.strip()

            if token is None:
                raise SyntaxError(message="Expected `end` before EOF").add(tokens=tokens, source=self.source)

            elif token.type == Tokens.end_kwd:
                tokens.append(self.next())
                break

            elif token.type == Tokens.def_kwd:
                value = self.parseMethod()

            elif token.type == Tokens.new_kwd:
                meth = self.parseConstructor()
                if constructor is not None:
                    constructor.assimilate(meth)
                else:
                    constructor = meth
                continue

            elif token.type == Tokens.identifier:
                value = self.parseVariable()

            else:
                self._unexpected(token)

            self.expect(Tokens.newline)
            self.addChild(attributes, value)

        return lekvar.Class(name, constructor, list(attributes.values()))

    def parseWhile(self):
        tokens = [self.next()]
        assert tokens[0].type == Tokens.while_kwd

        condition = self.parseValue()

        instructions = []

        while True:
            token = self.lookAhead()

            if token is None:
                raise SyntaxError(message="Expected `end` before EOF").add(tokens=tokens, source=self.source)

            elif token.type == Tokens.end_kwd:
                tokens.append(self.next())
                break

            instructions.append(self.parseLine())

        branch = lekvar.Branch(condition, [], lekvar.Branch(None, [lekvar.Break()]))
        return lekvar.Loop([branch] + instructions, tokens)

    def parseLoop(self):
        tokens = [self.next()]
        assert tokens[0].type == Tokens.loop_kwd

        instructions = []

        while True:
            token = self.lookAhead()

            if token is None:
                raise SyntaxError(message="Expected `end` before EOF").add(tokens=tokens, source=self.source)

            elif token.type == Tokens.end_kwd:
                tokens.append(self.next())
                break

            instructions.append(self.parseLine())

        return lekvar.Loop(instructions, tokens)

    def parseBreak(self):
        token = self.next()

        assert token.type == Tokens.break_kwd

        return lekvar.Break([token])

    def parseBranch(self, start_kwd = Tokens.if_kwd, has_condition = True):
        tokens = [self.next()]
        assert tokens[0].type == start_kwd

        condition = self.parseValue() if has_condition else None

        instructions = []
        next_branch = None

        while True:
            token = self.strip()

            if token is None:
                raise SyntaxError(message="Expected `end`, `else` or `elif` before EOF").add(tokens=tokens, source=self.source)

            elif token.type == Tokens.elif_kwd:
                next_branch = self.parseBranch(Tokens.elif_kwd)
                break

            elif token.type == Tokens.else_kwd:
                next_branch = self.parseBranch(Tokens.else_kwd, False)
                break

            elif token.type == Tokens.end_kwd:
                tokens.append(self.next())
                break

            instructions.append(self.parseLine())

        return lekvar.Branch(condition, instructions, next_branch, tokens)

    # Parse a variable, with optional type signature
    def parseVariable(self):
        tokens = []
        modifiers = []

        if self.lookAhead().type == Tokens.const_kwd:
            tokens.append(self.next())
            modifiers.append(lekvar.Constant)

        name = self.expect(Tokens.identifier, tokens).data

        type = self.parseTypeSig()

        value = lekvar.Variable(name, type, tokens)
        for mod in modifiers:
            value = mod(value)
        return value

    # Parse an optional type signature
    def parseTypeSig(self, typeof = Tokens.typeof):
        if self.lookAhead().type != typeof:
            return None
        self.next()

        return self.parseValue()

    def parseCall(self, called):
        tokens = [self.next()]
        assert tokens[0].type == Tokens.group_start

        arguments = []
        token = self.lookAhead()
        if token is None:
            self.expect(Tokens.group_end)

        if token.type != Tokens.group_end:

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

        return lekvar.Call(called, arguments, None, tokens)

    def parseReturn(self):
        # return keyword is expected to be parsed
        tokens = [self.next()]
        assert tokens[0].type == Tokens.return_kwd

        try:
            value = self.parseValue()
        except SyntaxError:
            value = None

        return lekvar.Return(value, tokens)

    def parseAssignment(self):
        # Find what's on the lhs
        lhs = self.parseVariable()

        tokens = [self.expect(Tokens.assign)]

        value = self.parseValue()
        return lekvar.Assignment(lhs, value, tokens)

    def parseAttribute(self, value):
        tokens = [self.expect(Tokens.dot)]

        attribute = self.expect(Tokens.identifier, tokens).data
        return lekvar.Attribute(value, attribute, tokens)

    def parseCast(self, value):
        token = self.next()
        assert token.type == Tokens.as_kwd

        type = self.parseSingleValue()
        return lekvar.Operation(lekvar.Attribute(value, token.data), [], type, [token])

    def parseImport(self):
        tokens = [self.next()]
        assert tokens[0].type == Tokens.import_kwd

        path = self.parseImportPath(tokens)

        name = None
        token = self.lookAhead()
        if token is not None and token.type == Tokens.as_kwd:
            tokens.append(self.next())

            name = self.expect(Tokens.identifier, tokens).data
        return lekvar.Import(path, name, tokens)

    def parseImportPath(self, tokens):
        path = []

        # Paths can start with any number of dots
        while self.lookAhead().type == Tokens.dot:
            tokens.append(self.next())
            path.append("..")

        # Then identifiers separated by dots
        while True:
            token = self.expect(Tokens.identifier, tokens)
            path.append(token.data)

            token = self.lookAhead()
            # Check for next path element
            if token is not None and token.type == Tokens.dot:
                tokens.append(self.next())
            # Otherwise stop parsing for a path
            else:
                return path
