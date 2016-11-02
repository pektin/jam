from ..errors import *

from .state import State
from .core import Context, Object, BoundObject, Scope, Type
from .closure import Closure
from .function import Function, FunctionType, Return
from .method import Method, MethodType
from .variable import Variable

class Class(Type, Closure):
    constructor = None
    instance_context = None
    type = None

    verified = False
    static = True
    static_scope = True

    def __init__(self, name:str, constructor:Method, attributes:[BoundObject], tokens = None):
        Closure.__init__(self, name, tokens)

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
            self.verifyNonRecursive()

    def resolveType(self):
        if self.type is None:
            self.type = MetaClass(self)
        return MetaClass(self)

    def verifyNonRecursive(self):
        # Traverse tree of class attributes, looking for self
        is_var = lambda a: isinstance(a, Variable)
        attributes = list(filter(is_var, self.instance_context))

        while len(attributes) > 0:
            attr = attributes.pop(0)
            type = attr.resolveType().resolveValue()

            if type is self:
                raise TypeError(object=self).add(message="is recursive, here").add(object=attr)
            elif isinstance(type, Class):
                attributes += list(filter(is_var, type.instance_context))

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

    def checkCompatibility(self, other:Type, check_cache = None) -> bool:
        return other.resolveValue() == self

    def __repr__(self):
        return "class {}".format(self.name)

class Constructor(Function):
    constructing = None

    def __init__(self, function:Function, constructing:Type, tokens = None):
        Function.__init__(self, function.name, function.arguments, function.instructions, [], constructing, tokens)
        self.local_context = function.local_context
        self.constructing = constructing

    def verifySelf(self):
        # Constructors may not return
        if State.soft_scope_state.maybe_returns:
            #TODO: Find returns
            raise SyntaxError(object=self).add(message="within a constructor is invalid")

class MetaClass(Class):
    class_instance = None

    def __init__(self, instance:Class):
        fields = []
        if instance.constructor is not None:
            constructor = Variable("", instance.constructor.resolveType())
            fields.append(constructor)
        Class.__init__(self, "meta " + instance.name, None, fields)

        self.class_instance = instance
        self.class_instance.instance_context.fakeChild(self)

    def __eq__(self, other):
        if isinstance(other, MetaClass):
            return self.class_instance == other.class_instance
        return False

    def __hash__(self):
        return hash(self.class_instance)

    @property
    def static(self):
        return self.class_instance.static
