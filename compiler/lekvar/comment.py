from .core import Context, Object, BoundObject, Type

class Comment(Object):
    contents = None

    def __init__(self, contents, tokens = None):
        super().__init__(tokens)
        self.contents = contents

    def copy(self):
        return Comment(self.contents)

    def verify(self):
        pass

    def resolveType(self):
        raise TypeError("Comments do not have a type")

    def __repr__(self):
        return "# {} #".format(self.contents)
