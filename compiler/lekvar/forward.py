from contextlib import contextmanager, ExitStack
from itertools import chain

from ..errors import *

from .state import State
from .core import Context, Object, BoundObject, Scope, Type
from .stats import Stats
from .util import inScope
from .links import Link

# Python Predefines
ForwardObject = None

# Apply targeting to a set of forward objects and their dependencies
@contextmanager
def target(objects:[(ForwardObject, Object)], checkTypes = True):
    with ExitStack() as stack:
        dependencies = iter(objects)
        while True:
            dep = next(dependencies, 0)
            if dep is 0: break
            if dep is None: continue

            object, target = dep
            next_dependencies = object.targetAt(target, checkTypes)
            dependencies = chain(dependencies, stack.enter_context(next_dependencies))

        yield

# A forward object is a collector for behaviour
# Initially the object is used like any other, creating dependencies
# Later a object can be chosen to "replace" the forward object,
# Which is then checked for all the dependencies.
# This is similar to templating, but much more powerful and less context
# forward.
class ForwardObject(Type, BoundObject):
    # The target object which which to replace the forward object
    target = None
    # The scope in which the forward object is mutable
    scope = None

    # Child Dependencies
    _context = None
    _instance_context = None
    resolved_type = None
    resolved_calls = None
    resolved_instance_calls = None

    # Object Dependencies
    target_switch = None
    target_switch_determiner = None
    compatible_types = None
    compatible_type_switch = None
    switches = None

    # Hack for forward functions
    _return_type = None

    def __init__(self, scope:Scope, name:str = None, tokens = None):
        BoundObject.__init__(self, name or "", tokens)
        self.scope = scope

        self.resolved_calls = dict()
        self.resolved_instance_calls = dict()
        self.compatible_types = set()
        self.switches = []

    def __eq__(self, other):
        if self.target is None:
            return Type.__eq__(self, other)
        return self.target == other.resolveValue()

    def __hash__(self):
        if self.target is None:
            return Type.__hash__(self)
        return hash(self.target)

    @classmethod
    def switch(self, scope:Scope, targets:[Object], determiner:(lambda Object: bool)):
        out = ForwardObject(scope)
        out.target_switch = targets
        out.target_switch_determiner = determiner
        return out

    @property
    def locked(self):
        return not inScope(self.scope, State.scope)

    @property
    def resolved(self):
        return self.target is not None

    def verify(self):
        if self.target: self.target.verify()

    # alias to the target if it exists
    def resolveValue(self):
        return self.target or self

    def extractValue(self):
        if self.target is None:
            return self
        return self.target

    # Targets this forward object
    @contextmanager
    def targetAt(self, target, checkTypes = True):
        if isinstance(target, ForwardObject):
            target = target.resolveValue()

        with ExitStack() as stack:
            #TODO: Handle errors

            # Escape recursion
            if self.target is not None:
                if self.target is target:
                    yield []
                    return

                #TODO: There should be a safer way to handle this

            # Local checks
            if checkTypes and not self.checkLockedCompatibility(target):
                raise TypeError(message="TODO: Write this")

            # Pass on dependency checks
            def target_generator():
                if self._context is not None:
                    yield self.context, target.context

                if self._instance_context is not None:
                    yield self.instance_context, target.instance_context

                if self.resolved_type is not None:
                    yield self.resolved_type, target.resolveType()

                calls = self._targetCall(target, self.resolved_calls, lambda c: c.resolveCall)
                inst_calls = self._targetCall(target, self.resolved_instance_calls, lambda o: o.resolveInstanceCall)
                for o in chain(calls, inst_calls):
                    yield o

                for switch in self.switches:
                    yield switch.resolveTarget()

                if self._return_type is not None:
                    # Should fail compatibility checks if not true
                    assert hasattr(target, "return_type")

                    yield self._return_type, target.return_type

            previous_target = self.target
            self.target = target
            yield target_generator()
            self.target = previous_target

    def _targetCall(self, target, calls, resolution_function):
        for call, obj in calls.items():
            target_call = resolution_function(target)(call)

            yield obj, target_call
            # The call itself may also be forward, so we have to target that
            if not all(arg.resolved for arg in call.arguments if isinstance(arg, ForwardObject)):
                for arg, target_arg in zip(call.arguments, target_call.arguments):
                    if isinstance(arg, ForwardObject):
                        yield arg, target_arg

    # Same as targetAt but for switches
    def resolveTarget(self):
        # It should already be verified that only one switch matches
        for possibility in self.target_switch:
            if self.target_switch_determiner(possibility):
                target = possibility
                break

        return self, target

    # Create and cache dependencies for standard object functionality
    @property
    def context(self):
        self._context = self._context or ForwardContext(self)
        return self._context

    @property
    def instance_context(self):
        self._instance_context = self._instance_context or ForwardContext(self)
        return self._instance_context

    def resolveType(self):
        if self.target is not None: return self.target.resolveType()

        self.resolved_type = self.resolved_type or ForwardObject(self.scope)
        return self.resolved_type

    def resolveCall(self, call):
        return self.resolved_calls.setdefault(call, ForwardObject(self.scope))

    def resolveInstanceCall(self, call):
        return self.resolved_instance_calls.setdefault(call, ForwardObject(self.scope))

    @property
    def stats(self):
        if self.target is None:
            if self._stats is None:
                self._stats = Stats(self.scope)
                self._stats.forward = True
            return self._stats

        return self.target.stats

    # Hack!
    @property
    def return_type(self):
        self._return_type = self._return_type or ForwardObject(self.scope)
        return self._return_type

    def checkCompatibility(self, other:Type, check_cache = None):
        if self is other.resolveValue(): return True
        if self.target is not None: return self.target.checkCompatibility(other, check_cache)
        if self.locked: return self.checkLockedCompatibility(other, check_cache)

        if State.type_switching:
            other = other.resolveValue()

            self.compatible_type_switch = self.compatible_type_switch or []
            self.compatible_type_switch.append(other)
            State.type_switch_cleanups.append(self.typeSwitchCleanup)
        else:
            self.compatible_types.add((other,))
        return True

    def revCheckCompatibility(self, other:Type, check_cache = None):
        if self is other.resolveValue(): return True
        if self.target is not None: return self.target.revCheckCompatibility(other, check_cache)

        # On reverse checks, we're always locked
        return self.checkLockedCompatibility(other, check_cache)

    def checkLockedCompatibility(self, other:Type, check_cache = None):
        other = other.resolveValue()
        # Keep a set of 'checked' types to escape infinite recursion
        if check_cache is None: check_cache = {}
        cache = check_cache.setdefault(self, set())

        if self is other:
            cache.add(other)
            return True

        for types in self.compatible_types:
            matches = []
            with State.type_switch():
                for type in types:
                    if type in cache:
                        matches.append(type)
                    else:
                        cache.add(type)
                        if checkCompatibility(type, other, check_cache):
                            matches.append(type)

            if not other.stats.forward and len(matches) != 1:
                return False
        return True

    def typeSwitchCleanup(self):
        if self.compatible_type_switch is None: return
        self.compatible_types.add(tuple(self.compatible_type_switch))
        self.compatible_type_switch = None

    def __repr__(self):
        if self.target is None:
            return "{}{{{}}}".format(self.__class__.__name__, self.name or id(self))
        return "{} as {}".format(self.__class__.__name__, self.target)


class ForwardTarget(Link):
    dependencies = None

    def __init__(self, value:Object, dependencies:[(ForwardObject, Object)], tokens = None):
        Link.__init__(self, value, tokens)
        self.dependencies = dependencies

    @contextmanager
    def target(self):
        with target(self.dependencies):
            yield

    def __repr__(self):
        return "FT({}, {})".format(self.value, self.dependencies)

# The forward context compliments the forward object with the creation
# of dependencies for contexts.
class ForwardContext(Context):
    def __init__(self, scope:BoundObject):
        Context.__init__(self, scope, [])

    def __contains__(self, name:str):
        if self.locked: return Context.__contains__(self, name)
        return True

    def __getitem__(self, name:str):
        if not self.locked and name not in self.children:
            self.addChild(ForwardObject(self.scope.scope, name))
        return self.children[name]

    def __setitem__(self, name:str, value:BoundObject):
        raise InternalError("Not Implemented.")

    @property
    def locked(self):
        return self.scope.locked

    @contextmanager
    def targetAt(self, target, checkTypes = True):
        def target_generator():
            if isinstance(target, ForwardContext) and self.scope.scope is target.scope.scope:
                target.scope._instance_context = self
                yield None
                return

            for name in self.children:
                if name not in target.children:
                    raise (DependencyError(message="Forward target context does not have attribute")
                           .add(content=name).add(message="", object=target.scope))
                yield self[name], target[name]
        yield target_generator()
