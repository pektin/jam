from ..errors import *

from .util import *
from .state import State
from .core import Context, Object, BoundObject, SoftScope, Scope, Type
from .util import checkCompatibility
from .links import BoundLink
from .variable import Variable
from .dependent import DependentObject

# Python Predefines
FunctionType = None

# A function is a single callable entity. It is defined through a set of inputs,
# a set of instructions, and a singular output.
class Function(Scope):
    local_context = None
    closed_context = None

    arguments = None
    instructions = None

    type = None
    verified = False
    static_scope = False

    def __init__(self, name:str, arguments:[Variable], instructions:[Object], children:[Object], return_type:Type = None, tokens = None):
        Scope.__init__(self, name, tokens)

        self.local_context = Context(self, arguments + children)
        self.closed_context = Context(self, [])

        self.arguments = arguments
        self.instructions = instructions

        for arg in self.arguments:
            if arg.resolveType() is None:
                arg.type = DependentObject(self)
                self.dependent = True

        self.type = FunctionType([arg.resolveType() for arg in arguments], return_type)

    def resolveIdentifier(self, name:str):
        found = BoundObject.resolveIdentifier(self, name)

        for match in found:
            if not match.static:
                self.closed_context.addChild(BoundLink(match))

        return found + SoftScope.resolveIdentifier(self, name)

    def verify(self):
        if self.verified: return
        self.verified = True

        # Arguments are considered to be already assigned
        for variable in self.arguments:
            variable.verifyAssignment(None)

        with State.scoped(self, analys = True):
            self.type.verify()

            for instruction in self.instructions:
                instruction.verify()

            # Analytical verification
            self.verifySelf()

    # Used to perform analytical verification after standard verification
    # Guaranteed to run within the scope of the function
    def verifySelf(self):
        # If we have a return type, we must return on all code paths
        if self.type.return_type is not None and not State.soft_scope_state.definately_returns:
            raise SemanticError(message="All code paths must return for").add(object=self)

    def resolveType(self):
        return self.type

    def resolveCall(self, call:FunctionType):
        if not checkCompatibility(self.resolveType(), call):
            raise TypeError(object=self).add(message="is not callable with").add(object=call)
        return self

    def __repr__(self):
        return "def {}({}) -> {}".format(self.name,
            (", ".join(str(arg) for arg in self.arguments)), self.type.return_type)

class FunctionType(Type):
    arguments = None
    return_type = None
    dependent = False

    verified = False

    def __init__(self, arguments:[Type], return_type:Type = None, tokens = None):
        Type.__init__(self, tokens)
        self.arguments = arguments
        self.dependent = any(isinstance(arg, DependentObject) for arg in arguments)
        self.return_type = return_type

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
                if not checkCompatibility(other_arg, self_arg):
                    return False

            # Only check for return type compatibility when the other has one
            if other.return_type is not None:
                # If this return type is none, not compatible
                if self.return_type is None:
                    return False

                return checkCompatibility(other.return_type, self.return_type)
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
        Object.__init__(self, tokens)
        self.value = value

    def verify(self):
        scope = State.soft_scope_state.scope

        if not isinstance(State.scope, Function):
            raise SyntaxError(message="Cannot").add(object=self).add(message="outside of a function")
        self.function = State.scope

        if self.value is not None:
            self.value.verify()

            # Infer function types
            if self.function.type.return_type is None:
                self.function.type.return_type = self.value.resolveType()
        # Check function types
            else:
                checkCompatibility(self.function.type.return_type, self.value.resolveType())
        elif self.function.type.return_type is not None:
            raise TypeError(object=self).add(message="must return a").add(object=self.function.type.return_type)

        # Update scope state
        State.soft_scope_state.definately_returns = True
        State.soft_scope_state.maybe_returns = True

    def resolveType(self):
        raise InternalError("Return objects do not have a type")

    def __repr__(self):
        return "return {}".format(self.value)
