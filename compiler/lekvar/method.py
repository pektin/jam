from ..errors import *

from .state import State
from .core import Context, Object, BoundObject, SoftScope, Type
from .util import checkCompatibility
from .function import Function, FunctionType
from .dependent import DependentObject, DependentTarget

# Python Predefines
Method = None

class Method(BoundObject, SoftScope):
    overload_context = None
    dependent_overload_context = None

    def __init__(self, name:str, overloads:[Function], tokens = None):
        BoundObject.__init__(self, name, tokens)

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
        return MethodType([fn.resolveType() for fn in self.overload_context],
                          [fn.resolveType() for fn in self.dependent_overload_context])

    def resolveCall(self, call:FunctionType):
        matches = []

        # Collect overloads which match the call type
        for overload in self.overload_context:
            if checkCompatibility(call, overload.resolveType()):
                matches.append(overload)

        # Check dependent types if no other ones were found
        if len(matches) == 0:
            for overload in self.dependent_overload_context:
                if checkCompatibility(call, overload.resolveType()):
                    matches.append(overload)

            if len(matches) == 1:
                return matches[0].dependentTarget(call)

        elif len(matches) > 1 and call.dependent and State.scope.dependent:
            fn = DependentObject.switch(self, matches, lambda overload: checkCompatibility(call, overload.resolveType()))
            # Find last argument that is dependent (the last one whose target is resolved)
            for arg in reversed(call.arguments):
                if isinstance(arg, DependentObject):
                    arg.switches.append(fn)
                    return fn

        # Allow only one match
        if len(matches) < 1:
            err = (TypeError(object=self).add(message="does not have an overload for")
                                         .add(object=call).addNote(message="Possible overloads:"))
            for overload in list(self.overload_context) + list(self.dependent_overload_context):
                err.addNote(object=overload, message="")
            raise err
        elif len(matches) > 1:
            err = (TypeError(message="Ambiguous call").add(object=call).add(message="to")
                                                      .add(object=self).add(message="Matches:"))
            for match in matches:
                err.addNote(object=match, message="")
            raise err

        return matches[0]

    @property
    def local_context(self):
        return None

    def __repr__(self):
        return "method {}".format(self.name)

class MethodType(Type):
    overloads = None
    used_overloads = None
    dependent_overloads = None
    used_dependent_overloads = None
    dependent = False

    def __init__(self, overloads:[FunctionType], dependent_overloads:[FunctionType], tokens = None):
        Type.__init__(self, tokens)
        self.overloads = overloads
        self.used_overloads = {}
        self.dependent_overloads = dependent_overloads
        self.used_dependent_overloads = {}
        self.dependent = len(dependent_overloads) > 0

    def resolveType(self):
        raise InternalError("Not Implemented")

    def verify(self):
        for fn_type in self.overloads + self.dependent_overloads:
            fn_type.verify()

    @property
    def local_context(self):
        raise InternalError("Not Implemented")

    def checkCompatibility(self, other:Type, check_cache = None):
        if not isinstance(other, MethodType):
            return False

        for self_fn_type in self.overloads:
            compat_fn_type = None
            for other_fn_type in other.overloads:
                if self_fn_type.checkCompatibility(other_fn_type, check_cache):
                    compat_fn_type = other_fn_type
                    break

            if compat_fn_type is None:
                if self_fn_type in self.used_overloads:
                    return False
                else:
                    pass
            #TODO: More type checks

        for self_fn_type in self.dependent_overloads:
            for other_fn_type in other.overloads:
                if self_fn_type.checkCompatibility(other_fn_type, check_cache):
                    #TODO: Actually check these
                    pass

        return True

    def resolveInstanceCall(self, call:FunctionType):
        matches = []

        for fn_type in self.overloads:
            if fn_type.checkCompatibility(call):
                matches.append(fn_type)

        if len(matches) == 0:
            for fn_type in self.dependent_overloads:
                if fn_type.checkCompatibility(call):
                    matches.append(fn_type)

            if len(matches) == 1:
                self.used_dependent_overloads[call] = True
                return MethodInstance(self, call)

        elif len(matches) == 1:
            self.used_overloads[matches[0]] = True
            return MethodInstance(self, matches[0])

        raise TypeError(message="TODO: Write This")

    @property
    def used_overload_types(self):
        return [type for type, used in self.used_overloads.items() if used]

    @property
    def used_dependent_overload_types(self):
        return [type for type, used in self.used_dependent_overloads.items() if used]

class MethodInstance(Object):
    def __init__(self, type:MethodType, target:FunctionType):
        Object.__init__(self)
        self.type = type
        self.target = target

    def verify(self):
        self.type.verify()

    def resolveType(self):
        return self.target

    def resolveCall(self, call:FunctionType):
        return self

    @property
    def context(self):
        return None

    def __repr__(self):
        return "MethodInstance({})".format(self.resolveType())
