from ..errors import *

from .state import State
from .core import Context, Object, BoundObject, Type
from .util import checkCompatibility
from .variable import Variable
from .dependent import DependentType

# Python Predefines
FunctionType = None


class Function(BoundObject):
    _local_context = None
    closed_context = None

    arguments = None
    instructions = None

    type = None
    dependent = False
    verified = False
    static = False

    def __init__(self, name:str, arguments:[Variable], instructions:[Object], return_type:Type = None, tokens = None):
        super().__init__(name, tokens)

        self._local_context = Context(self, arguments)
        self.closed_context = Context(self, [])

        self.arguments = arguments
        self.instructions = instructions

        for arg in self.arguments:
            if arg.type is None:
                arg.type = DependentType()
                self.dependent = True

        self.type = FunctionType(name, [arg.type for arg in arguments], return_type)

    @property
    def local_context(self):
        return self._local_context

    def copy(self):
        fn = Function(self.name, list(map(copy, self.arguments)), list(map(copy, self.instructions)), self.type.return_type)
        fn.static = self.static
        return fn

    def verify(self):
        if self.verified: return
        self.verified = True

        with State.scoped(self):
            self.type.verify()

            for instruction in self.instructions:
                instruction.verify()

            # Further, analytical verification
            self.verifySelf()

    def verifySelf(self):
        # Ensure non-void functions return
        if not any(isinstance(inst, Return) for inst in self.instructions) and self.type.return_type is not None:
            raise SemanticError("All code paths must return", self.tokens)

    def resolveType(self):
        return self.type

    def resolveCall(self, call:FunctionType):
        if not checkCompatibility(self.resolveType(), call):
            raise TypeError("Function is not callable with {}".format(call), self.tokens)

        if not self.dependent:
            return self

        # Create a template instance
        fn = copy(self)
        for index, arg in enumerate(fn.arguments):
            if isinstance(arg.type, DependentType):
                fn.type.arguments[index] = arg.type.target = call.arguments[index]
        fn.verify()
        return fn

    def __repr__(self):
        return "def {}({}) -> {}".format(self.name,
            (", ".join(str(arg) for arg in self.arguments)), self.type.return_type)

class FunctionType(Type):
    arguments = None
    return_type = None

    verified = False

    def __init__(self, name:str, arguments:[Type], return_type:Type = None, tokens = None):
        super().__init__(name, tokens)
        self.arguments = arguments
        self.return_type = return_type

    def copy(self):
        return FunctionType(self.name, list(map(copy, self.arguments)), copy(self.return_type))

    def verify(self):
        if self.verified: return
        self.verified = True

        for arg in self.arguments:
            arg.verify()
        if self.return_type is not None:
            self.return_type.verify()

    def resolveType(self):
        raise InternalError("Not Implemented")

    @property
    def local_context(self):
        raise InternalError("Not Implemented")

    def checkCompatibility(self, other:Type):
        other = other.resolveValue()

        if isinstance(other, FunctionType):
            if len(self.arguments) != len(other.arguments):
                return False

            for self_arg, other_arg in zip(self.arguments, other.arguments):
                if not self_arg.checkCompatibility(other_arg):
                    return other_arg.checkCompatibility(self_arg)

            return True
        return False

    def __repr__(self):
        return "({}) -> {}".format(", ".join(repr(arg) for arg in self.arguments), self.return_type)

#
# Return
#
# Returns can only exist as instructions for functions. They cause the function
# to return with a specified value.

class Return(Object):
    value = None
    function = None

    def __init__(self, value:Object = None, tokens = None):
        super().__init__(tokens)
        self.value = value

    def copy(self):
        return Return(copy(self.value))

    def verify(self):
        self.value.verify()

        if not isinstance(State.scope, Function):
            raise SyntaxError("Cannot return outside of a function", self.tokens)
        self.function = State.scope

        # Infer function types
        if self.function.type.return_type is None:
            self.function.type.return_type = self.value.resolveType()
        else:
            checkCompatibility(self.function.type.return_type, self.value.resolveType())

    def resolveType(self):
        return None

    def __repr__(self):
        return "return {}".format(self.value)
