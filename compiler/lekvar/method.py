from ..errors import *

from .state import State
from .stats import Stats, ScopeStats
from .core import Context, Object, BoundObject, SoftScope, Scope, Type
from .util import checkCompatibility
from .function import Function, FunctionType, FunctionInstance
from .forward import ForwardObject, ForwardTarget

# Python Predefines
Method = None

class Method(Scope):
    verified = False
    overload_context = None

    def __init__(self, name:str, overloads:[Function], tokens = None):
        BoundObject.__init__(self, name, tokens)

        self.overload_context = Context(self, [])
        for overload in overloads:
            self.addOverload(overload)

    # Pre-verification method
    def addOverload(self, overload:Function):
        overload.name = str(len(self.overload_context))
        self.overload_context.addChild(overload)

    # Pre-verification method
    def assimilate(self, other:Method):
        for overload in other.overload_context:
            self.addOverload(overload)

    def verify(self):
        if self.verified: return
        self.verified = True

        self._stats = ScopeStats(self.parent)

        with State.scoped(self):
            self.overload_context.verify()

    def resolveType(self):
        return MethodType([fn.resolveType() for fn in self.overload_context])

    def resolveCall(self, call:FunctionType):
        matches = []

        # Collect overloads which match the call type
        for overload in self.overload_context:
            overload.verify()
            if checkCompatibility(call, overload.resolveType()):
                matches.append(overload)

        normal_matches = [match for match in matches if not match.stats.forward]
        forward_matches = [match for match in matches if match.stats.forward]

        # Check forward types if no other ones were found
        if len(normal_matches) == 0:
            if len(forward_matches) == 1:
                return forward_matches[0].forwardTarget(call)
            else:
                normal_matches = forward_matches

        elif len(normal_matches) > 1 and call.stats.forward:# and State.scope.stats.forward:
            fn = ForwardObject.switch(self, matches, lambda overload: checkCompatibility(call, overload.resolveType()))
            # Find last argument that is forward (the last one whose target is resolved)
            for arg in reversed(call.arguments):
                if arg.stats.forward:
                    forward = arg.extractValue()
                    assert isinstance(forward, ForwardObject)
                    forward.switches.append(fn)
                    return fn
            raise InternalError()

        # Allow only one match
        if len(normal_matches) < 1:
            err = (TypeError(object=self).add(message="does not have an overload for")
                                         .add(object=call).addNote(message="Possible overloads:"))
            for overload in self.overload_context:
                err.addNote(object=overload, message="")
            raise err
        elif len(normal_matches) > 1:
            err = (TypeError(message="Ambiguous call").add(object=call).add(message="to")
                                                      .add(object=self).add(message="Matches:"))
            for match in normal_matches:
                err.addNote(object=match, message="")
            raise err

        return normal_matches[0]

    @property
    def local_context(self):
        return None

    def __repr__(self):
        return "method {}".format(self.name)

class MethodType(Type):
    overloads = None
    used_overloads = None

    def __init__(self, overloads:[FunctionType], tokens = None):
        Type.__init__(self, tokens)
        self.overloads = overloads
        self.used_overloads = {}

    def resolveType(self):
        raise InternalError("Not Implemented")

    def verify(self):
        self._stats = Stats(None)
        self._stats.static = True

        for fn_type in self.overloads:
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

        # for self_fn_type in self.forward_overloads:
        #     for other_fn_type in other.overloads:
        #         if self_fn_type.checkCompatibility(other_fn_type, check_cache):
        #             #TODO: Actually check these
        #             pass

        return True

    def resolveInstanceCall(self, call:FunctionType):
        matches = []

        for fn_type in self.overloads:
            if fn_type.checkCompatibility(call):
                matches.append(fn_type)

        normal_matches = [match for match in matches if not match.stats.forward]
        forward_matches = [match for match in matches if match.stats.forward]

        if len(normal_matches) == 0:
            if len(forward_matches) == 1:
                self.used_overloads[call] = True
                return MethodInstance(self, call)
            else:
                normal_matches = forward_matches

        elif len(normal_matches) == 1:
            self.used_overloads[normal_matches[0]] = True
            return MethodInstance(self, normal_matches[0])

        raise TypeError(message="TODO: Write This")

    @property
    def used_overload_types(self):
        return [type for type, used in self.used_overloads.items() if used]

class MethodInstance(Object):
    def __init__(self, type:MethodType, target_type:FunctionType):
        Object.__init__(self)
        self.type = type
        self.target = FunctionInstance(target_type)

    def verify(self):
        self.type.verify()

    def resolveType(self):
        return self.target.type

    def resolveCall(self, call:FunctionType):
        return self

    @property
    def context(self):
        return None

    def __repr__(self):
        return "MethodInstance({})".format(self.resolveType())
