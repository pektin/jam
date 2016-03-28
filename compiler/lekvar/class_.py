from ..errors import *

from .state import State
from .core import Context, Object, BoundObject, Scope, Type
from .function import Function, FunctionType, Return
from .method import Method, MethodType
from .variable import Variable

class Class(Type, Scope):
    constructor = None
    instance_context = None

    verified = False
    static_scope = False

    def __init__(self, name:str, constructor:Method, attributes:[BoundObject], tokens = None):
        Scope.__init__(self, name, tokens)

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
            raise TypeError(object=self).add(message="does not have a constructor")
        return self.constructor.resolveCall(call)

    def resolveInstanceCall(self, call:FunctionType):
        if "" not in self.instance_context:
            raise TypeError(object=self).add(message="does not overload call operator")
        return self.instance_context[""].resolveCall(call)

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
        Function.__init__(self, function.name, function.arguments, function.instructions, [], constructing, tokens)
        self.local_context = function.local_context

    def verifySelf(self):
        # Constructors may not return
        if State.soft_scope_state.maybe_returns:
            #TODO: Find returns
            raise SyntaxError(object=self).add(message="within a constructor is invalid")
