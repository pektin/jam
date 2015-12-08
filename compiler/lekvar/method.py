from ..errors import *

from .state import State
from .core import Context, Object, BoundObject, Type
from .function import Function, FunctionType
from .dependent import DependentObject, DependentTarget

# Python Predefines
Method = None

class Method(BoundObject):
    overload_context = None
    dependent_overload_context = None

    def __init__(self, name:str, overloads:[Function], tokens = None):
        super().__init__(name, tokens)

        self.overload_context = Context(self, [])
        self.dependent_overload_context = Context(self, [])
        for overload in overloads:
            self.addOverload(overload)

    def addOverload(self, overload:Function):
        context = self.overload_context
        if overload.dependent:
            context = self.dependent_overload_context

        overload.name = str(len(context.children))
        context.addChild(overload)

    def assimilate(self, other:Method):
        for overload in other.overload_context:
            self.addOverload(overload)

        for overload in other.dependent_overload_context:
            self.addOverload(overload)

    def verify(self):
        with State.scoped(self):
            self.overload_context.verify()
            self.dependent_overload_context.verify()

    def resolveType(self):
        return MethodType([fn.resolveType() for fn in self.overload_context])

    def resolveCall(self, call:FunctionType):
        matches = []

        # Collect overloads which match the call type
        for overload in self.overload_context:
            if overload.resolveType().checkCompatibility(call):
                matches.append(overload)

        # Check dependent types if no other ones were found
        if len(matches) == 0:
            for overload in self.dependent_overload_context:
                if overload.resolveType().checkCompatibility(call):
                    matches.append(overload)

            if len(matches) == 1:
                fn = matches[0]
                args = [(arg_t, call_t) for arg_t, call_t in zip(fn.type.arguments, call.arguments)
                                if isinstance(arg_t, DependentObject)]
                return DependentTarget(fn, args)

        elif len(matches) > 1 and call.dependent and State.scope.dependent:
            fn = DependentObject.switch(self, matches, lambda overload: overload.resolveType().checkCompatibility(call))
            # Find last argument that is dependent (the last one whose target is resolved)
            for arg in reversed(call.arguments):
                if isinstance(arg, DependentObject):
                    arg.switches.append(fn)
                    return fn

        # Allow only one match
        if len(matches) < 1:
            err = TypeError(object=self).add(message="does not have an overload for").add(object=call).addNote(message="Possible overloads:")
            for overload in list(self.overload_context) + list(self.dependent_overload_context):
                err.addNote(object=overload)
            raise err
        elif len(matches) > 1:
            err = TypeError(message="Ambiguous call to").add(object=self).add(message="Matches:")
            for match in matches:
                err.addNote(object=match)
            raise err

        return matches[0]

    @property
    def local_context(self):
        return None

    def __repr__(self):
        return "method {}".format(self.name)

class MethodType(Type):
    overload_types = None
    used_overload_types = None

    def __init__(self, overloads:[FunctionType], tokens = None):
        super().__init__(tokens)
        self.overload_types = overloads
        self.used_overload_types = { fn_type: False for fn_type in overloads }

    def resolveType(self):
        raise InternalError("Not Implemented")

    def verify(self):
        for fn_type in self.overload_types:
            fn_type.verify()

    @property
    def local_context(self):
        raise InternalError("Not Implemented")

    def checkCompatibility(self, other:Type):
        if not isinstance(other, MethodType):
            return False

        for self_fn_type in self.overload_types:
            compat_fn_type = None
            for other_fn_type in other.overload_types:
                if self_fn_type.checkCompatibility(other_fn_type):
                    compat_fn_type = other_fn_type
                    break

            if compat_fn_type is None:
                if self.used_overload_types[self_fn_type]:
                    return False
                else:
                    pass
            #TODO: More type checks
        return True

    def resolveInstanceCall(self, call:FunctionType):
        matches = []
        for index in range(len(self.overload_types)):
            fn_type = self.overload_types[index]
            if fn_type.checkCompatibility(call):
                matches.append((fn_type, index))

        if len(matches) == 1:
            return MethodInstance(self, matches[0][1])
        raise TypeError(message="TODO: Write This")

class MethodInstance(Object):
    def __init__(self, type:MethodType, target:int):
        super().__init__()
        self.type = type
        self.target = target

    def verify(self):
        self.type.verify()

    def resolveType(self):
        return self.type.overload_types[self.target]

    def resolveCall(self, call:FunctionType):
        return self

    @property
    def context(self):
        return None
