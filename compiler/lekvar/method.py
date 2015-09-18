from ..errors import *

from .state import State
from .core import Context, Object, BoundObject, Type
from .function import Function, FunctionType
from .dependent import DependentObject, DependentTarget

# Python Predefines
Method = None

class Method(BoundObject):
    overload_context = None
    dependent_overload_context = None
    type = None

    def __init__(self, name:str, overloads:[Function], tokens = None):
        super().__init__(name, tokens)

        self.overload_context = Context(self, [])
        self.dependent_overload_context = Context(self, [])
        for overload in overloads:
            self.addOverload(overload)

    def addOverload(self, overload:Function):
        context = self.overload_context
        if overload.dependent:
            context = self.dependent_overload_context

        overload.name = str(len(context.children))
        context.addChild(overload)

    def assimilate(self, other:Method):
        for overload in other.overload_context:
            self.addOverload(overload)

        for overload in other.dependent_overload_context:
            self.addOverload(overload)

    def verify(self):
        with State.scoped(self):
            self.overload_context.verify()
            self.dependent_overload_context.verify()

    def resolveType(self):
        if self.type is None:
            self.type = MethodType(self.name, [fn.resolveType() for fn in self.overload_context])
        return self.type

    def resolveCall(self, call:FunctionType):
        matches = []

        # Collect overloads which match the call type
        for overload in self.overload_context:
            if overload.resolveType().checkCompatibility(call):
                matches.append(overload)

        # Check dependent types if no other ones were found
        if len(matches) == 0:
            with State.type_switch():
                for overload in self.dependent_overload_context:
                    if overload.resolveType().checkCompatibility(call):
                        matches.append(overload)
            if len(matches) == 1:
                args = [(matches[0].type.arguments[i], call.arguments[i])
                            for i in range(len(call.arguments))
                                if isinstance(matches[0].type.arguments[i], DependentObject)]
                return DependentTarget(overload, args)
        elif len(matches) > 1 and call.dependent:
            fn = DependentObject.switch(self, matches, lambda overload: overload.resolveType().checkCompatibility(call))
            # Find last argument that is dependent (the last one whose target is resolved)
            for arg in reversed(call.arguments):
                if isinstance(arg, DependentObject):
                    arg.switches.append(fn)
                    return fn

        # Allow only one match
        if len(matches) < 1:
            raise TypeError(
                [("Method does not have an overload for {}\nPossible overloads:".format(call), [])] +
                [("", overload.tokens) for overload in self.overload_context] +
                [("", overload.tokens) for overload in self.dependent_overload_context]
            )
        elif len(matches) > 1:
            raise TypeError(
                [("Ambiguous overloads for {}\nMatches:".format(call), [])] +
                [("", match.tokens) for match in matches]
            )

        return matches[0]

    @property
    def local_context(self):
        return None

    def __repr__(self):
        return "method {}".format(self.name)

class MethodType(Type):
    overloads = None

    def __init__(self, name:str, overloads:[FunctionType], tokens = None):
        super().__init__(name, tokens)
        self.overloads = overloads

    def resolveType(self):
        raise InternalError("Not Implemented")

    def verify(self):
        raise InternalError("Not Implemented")

    @property
    def local_context(self):
        raise InternalError("Not Implemented")

    def checkCompatibility(self, other:Type):
        return False #TODO: Check for identical overloads
