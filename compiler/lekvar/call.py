from .core import Context, Object, BoundObject, Type
from .function import FunctionType

class Call(Object):
    called = None
    values = None
    function = None

    def __init__(self, called:Object, values:[Object], tokens = None):
        super().__init__(tokens)
        self.called = called
        self.values = values
        self.function = None

    def copy(self):
        return Call(copy(self.called), list(map(copy, self.values)))

    def verify(self):
        super().verify()

        self.called.verify()

        # Verify arguments and create the function type of the call
        arg_types = []
        for val in self.values:
            val.verify()
            arg_types.append(val.resolveType())
        call_type = FunctionType("", arg_types)

        # Resolve the call
        self.function = self.called.resolveCall(call_type)

    def resolveType(self):
        return self.function.resolveType().return_type

    def __repr__(self):
        return "{}({})".format(self.called, ", ".join(repr(val) for val in self.values))
