from .state import State
from .core import Context, Object, BoundObject, Type
from .function import Function, FunctionType

# Python Predefines
Method = None

class Method(BoundObject):
    overload_context = None
    verified = False
    type = None

    def __init__(self, name:str, overloads:[Function], tokens = None):
        super().__init__(name, tokens)

        self.overload_context = Context(self, [])
        for overload in overloads:
            self.addOverload(overload)

    def copy(self):
        return Method(self.name, list(map(copy, self.overload_context.children.values())))

    def addOverload(self, overload:Function):
        overload.name = str(len(self.overload_context.children))
        self.overload_context.addChild(overload)

    def assimilate(self, other:Method):
        for overload in other.overload_context:
            self.addOverload(overload)

    def verify(self):
        if self.verified: return
        self.verified = True

        with State.scoped(self):
            self.overload_context.verify()

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

        # Allow only one match
        if len(matches) < 1:
            raise TypeError(("Method does not have an overload for {}\nPossible overloads:".format(call), []),
                (("", overload.tokens) for overload in self.overload_context)
            )
        elif len(matches) > 1 and not State.scope.dependent:
            raise TypeError(("Ambiguous overloads for {}\nMatches:".format(call), []),
                (("", match.tokens) for match in matches)
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

    # Method types are singletons
    def copy(self):
        return self

    def resolveType(self):
        raise InternalError("Not Implemented")

    def verify(self):
        pass

    def checkCompatibility(self, other:Type):
        return False #TODO: Check for identical overloads
