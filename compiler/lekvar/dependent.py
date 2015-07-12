from .core import Context, Object, BoundObject, Type

class DependentObject(Type):
    compatibles = None
    target = None

    def __init__(self, compatibles:[Type] = None, tokens = None):
        super().__init__("", tokens)

        if compatibles is None: compatibles = []
        self.compatibles = compatibles

    def copy(self):
        return DependentObject(self.compatibles[:])

    def verify(self):
        pass

    def checkCompatibility(self, other:Type):
        # If dependent type is targeted, only check for the target type
        if self.target is not None:
            return self.target.checkCompatibility(other)

        # Check with all compatible types
        #for type in self.compatibles:
        #    if not type.checkCompatibility(other):
        #        return False

        if other not in self.compatibles:
            self.compatibles.append(other)

        return True

    def resolveType(self):
        raise InternalError("Not Implemented")

    def __repr__(self):
        if self.target is None:
            return "{}<{}>".format(self.__class__.__name__, self.compatibles)
        else:
            return "{} as {}".format(self.__class__.__name__, self.target)
