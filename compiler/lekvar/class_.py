from ..errors import *

from .state import State
from .core import Context, Object, BoundObject, Type
from .function import Function, FunctionType, Return
from .method import Method, MethodType
from .variable import Variable

class Class(Type):
    constructor = None
    instance_context = None

    verified = False

    def __init__(self, name:str, constructor:Method, attributes:[BoundObject], tokens = None):
        super().__init__(name, tokens)

        self.instance_context = Context(self, attributes)

        # Convert constructor method of functions to method of constructors
        #TODO: Eliminate the need for this
        if constructor is not None:
            self.constructor = constructor
            for overload in self.constructor.overload_context:
                name = overload.name
                self.constructor.overload_context[name] = Constructor(overload, self)
                self.constructor.overload_context[name].bound_context = self.constructor.overload_context
                self.constructor.overload_context[name].closed_context.addChild(Variable("self", self))
            self.instance_context.fakeChild(self.constructor)

        for child in self.instance_context:
            if isinstance(child, Method):
                for overload in child.overload_context:
                    overload.closed_context.addChild(Variable("self", self))

    def copy(self):
        return Class(self.name, copy(self.constructor), list(map(copy, self.constructor.overload_context.children.values())))

    def verify(self):
        if self.verified: return
        self.verified = True

        with State.scoped(self):
            if self.constructor is not None:
                self.constructor.verify()

        self.instance_context.verify()

    def resolveType(self):
        raise InternalError("Not Implemented")

    def resolveCall(self, call:FunctionType):
        if self.constructor is None:
            raise TypeError("Class does not have a constructor".format(self), self.tokens)
        return self.constructor.resolveCall(call)

    @property
    def local_context(self):
        return self.instance_context

    def checkCompatibility(self, other:Type) -> bool:
        return other.resolveValue() is self

    def __repr__(self):
        contents = "\n".join(repr(val) for val in [self.constructor] + list(self.instance_context))
        return "class {}\n{}\nend".format(self.name, contents)

class Constructor(Function):
    def __init__(self, function:Function, constructing:Type, tokens = None):
        if function.type.return_type is not None:
            raise TypeError("Constructors must return nothing", function.tokens)
        function.type.return_type = constructing

        super().__init__(function.name, function.arguments, function.instructions, function.type.return_type, tokens)

    def verifySelf(self):
        for instruction in self.instructions:
            if isinstance(instruction, Return):
                raise SyntaxError("Returns within constructors are invalid", instruction.tokens)
