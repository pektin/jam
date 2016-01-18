from .core import Context, Object, BoundObject, Type

class Literal(Object):
    data = None
    type = None

    def __init__(self, data, type:Type, tokens = None):
        Object.__init__(self, tokens)
        self.data = data
        self.type = type

    def verify(self):
        Object.verify(self)

        self.type.verify()

    def resolveType(self):
        return self.type

    def __repr__(self):
        return "{}({})".format(self.type, self.data)
