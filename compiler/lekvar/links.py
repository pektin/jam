from .core import Context, Object, BoundObject, Type
from .util import resolveReference, resolveAttribute
from .function import Function, FunctionType

class Reference(Type):
    reference = None
    value = None

    verified = False

    def __init__(self, reference:str, tokens = None):
        super().__init__(tokens)
        self.reference = reference

    def copy(self):
        return Reference(self.reference)

    def verify(self):
        if self.verified: return
        self.verified = True

        # Resolve the reference using general reference resolution
        self.value = resolveReference(self.reference)
        self.value.verify()

    def resolveType(self):
        return self.value.resolveType()

    @property
    def local_context(self):
        return self.value.local_context

    @property
    def context(self):
        return self.value.context

    @property
    def instance_context(self):
        return self.value.instance_context

    def resolveCall(self, call:FunctionType):
        return self.value.resolveCall(call)

    def resolveValue(self):
        return self.value.resolveValue()

    def checkCompatibility(self, other:Type):
        return self.value.checkCompatibility(other)

    def __repr__(self):
        return "{}".format(self.reference)

class Attribute(Type):
    value = None
    reference = None
    attribute = None

    verified = False

    def __init__(self, value:Object, reference:str, tokens = None):
        super().__init__(tokens)
        self.value = value
        self.reference = reference

    def copy(self):
        return Attribute(self.value, self.reference)

    def verify(self):
        if self.verified: return
        self.verified = True

        self.value.verify()
        # Resolve the attribute using the values attribute resolution
        self.attribute = resolveAttribute(self.value, self.reference)
        self.attribute.verify()

        if self.attribute is None:
            raise MissingReferenceError("{} does not have an attribute {}".format(self.value, self.reference))

    @property
    def local_context(self):
        return self.attribute.local_context

    @property
    def context(self):
        return self.attribute.context

    @property
    def instance_context(self):
        return self.attribute.instance_context

    def resolveType(self):
        return self.attribute.resolveType()

    def resolveCall(self, call:FunctionType):
        return self.attribute.resolveCall(call)

    def resolveValue(self):
        return self.attribute.resolveValue()

    def checkCompatibility(self, other:Type):
        return self.attribute.checkCompatibility(other)

    def __repr__(self):
        return "{}.{}".format(self.value, self.reference)
