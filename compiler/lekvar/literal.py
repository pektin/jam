from .core import Context, Object, BoundObject, Type

class Literal(Object):
    data = None
    type = None

    def __init__(self, data, type:Type, tokens = None):
        super().__init__(tokens)
        self.data = data
        self.type = type

    def copy(self):
        return self

    def verify(self):
        super().verify()

        self.type.verify()

    def resolveType(self):
        return self.type

    def __repr__(self):
        return "{}({})".format(self.type, self.data)
