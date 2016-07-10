from contextlib import contextmanager, ExitStack
from itertools import chain

from ..errors import *

from .state import State
from .core import Context, Object, BoundObject, Scope, Type
from .util import inScope
from .links import Link

# Like util.checkCompatibility, but type1 can be dependent whose compatibility check takes more arguments
def checkDependentCompatibility(type1:Type, type2:Type, *args):
    if isinstance(type1, DependentObject):
        return type1.checkCompatibility(type2, *args)
    return type1.checkCompatibility(type2)

# A dependent object is a collector for behaviour
# Initially the object is used like any other, creating dependencies
# Later a object can be chosen to "replace" the dependent object,
# Which is then checked for all the dependencies.
# This is similar to templating, but much more powerful and less context
# dependent.
class DependentObject(Type, BoundObject):
    dependent = True

    # The target object which which to replace the dependent object
    target = None
    # The scope in which the dependent object is mutable
    scope = None

    # Child Dependencies
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

    # Hack for dependent functions
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
        out = DependentObject(scope)
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

    # Targets this dependent object
    @contextmanager
    def targetAt(self, target):
        if isinstance(target, DependentObject):
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
            if not self.checkLockedCompatibility(target):
                raise TypeError(message="TODO: Write this")

            # Pass on dependency checks
            def target_generator():
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

            self.target = target
            yield target_generator()
            self.target = None

    def _targetCall(self, target, calls, resolution_function):
        for call, obj in calls.items():
            target_call = resolution_function(target)(call)

            yield obj, target_call
            # The call itself may also be dependent, so we have to target that
            if not all(arg.resolved for arg in call.arguments if isinstance(arg, DependentObject)):
                for arg, target_arg in zip(call.arguments, target_call.arguments):
                    if isinstance(arg, DependentObject):
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
    def instance_context(self):
        self._instance_context = self._instance_context or DependentContext(self)
        return self._instance_context

    def resolveType(self):
        if self.target is not None: return self.target.resolveType()

        self.resolved_type = self.resolved_type or DependentObject(self.scope)
        return self.resolved_type

    def resolveCall(self, call):
        return self.resolved_calls.setdefault(call, DependentObject(self.scope))

    def resolveInstanceCall(self, call):
        return self.resolved_instance_calls.setdefault(call, DependentObject(self.scope))

    # Can be ignored, as context is superseded by instance_context
    @property
    def context(self):
        pass

    @property
    def static(self):
        return self.target.static

    @property
    def static_scope(self):
        return self.target.static_scope

    # Hack!
    @property
    def return_type(self):
        self._return_type = self._return_type or DependentObject(self.scope)
        return self._return_type

    def checkCompatibility(self, other:Type, check_cache = None):
        if self is other.resolveValue(): return True
        if self.target is not None: return checkDependentCompatibility(self.target, other, check_cache)
        if self.locked: return self.checkLockedCompatibility(other, check_cache)

        if State.type_switching:
            self.compatible_type_switch = self.compatible_type_switch or []
            self.compatible_type_switch.append(other)
            State.type_switch_cleanups.append(self.typeSwitchCleanup)
        else:
            self.compatible_types.add((other,))
        return True

    def revCheckCompatibility(self, other:Type, check_cache = None):
        if self is other.resolveValue(): return True
        if self.target is not None: return self.target.revCheckCompatibility(other)

        # On reverse checks, we're always locked
        return self.checkLockedCompatibility(other, check_cache)

    def checkLockedCompatibility(self, other:Type, check_cache = None):
        other = other.resolveValue()
        # Keep a set of 'checked' types to escape infinite recursion
        if check_cache is None: check_cache = {}
        cache = check_cache.setdefault(self, set())

        for types in self.compatible_types:
            matches = []
            for type in types:
                if type in cache:
                    matches.append(type)
                else:
                    cache.add(type)
                    if checkDependentCompatibility(type, other, check_cache):
                        matches.append(type)

            if len(matches) != 1:
                return False
        return True

    def typeSwitchCleanup(self):
        if self.compatible_type_switch is None: return
        self.compatible_types.add(tuple(self.compatible_type_switch))
        self.compatible_type_switch = None

    def __repr__(self):
        if self.target is None:
            return "{}".format(self.__class__.__name__)
        return "{} as {}".format(self.__class__.__name__, self.target)


class DependentTarget(Link):
    dependencies = None

    def __init__(self, value:Object, dependencies:[(DependentObject, Object)], tokens = None):
        Link.__init__(self, value, tokens)
        self.dependencies = dependencies

    @contextmanager
    def target(self):
        with ExitStack() as stack:
            dependencies = iter(self.dependencies)
            while True:
                dep = next(dependencies, 0)
                if dep is 0: break
                if dep is None: continue

                object, target = dep
                next_dependencies = object.targetAt(target)
                dependencies = chain(dependencies, stack.enter_context(next_dependencies))

            yield

    def __repr__(self):
        return "Target({}, {})".format(self.value, self.dependencies)

# The dependent context compliments the dependent object with the creation
# of dependencies for contexts.
class DependentContext(Context):
    dependent = True

    def __init__(self, scope:BoundObject):
        Context.__init__(self, scope, [])

    def __contains__(self, name:str):
        if self.scope.locked: return Context.__contains__(self, name)
        return True

    def __getitem__(self, name:str):
        if not self.scope.locked and name not in self.children:
            self.addChild(DependentObject(self.scope.scope, name))
        return self.children[name]

    def __setitem__(self, name:str, value:BoundObject):
        raise InternalError("Not Implemented.")

    @contextmanager
    def targetAt(self, target):
        def target_generator():
            if isinstance(target, DependentContext) and self.scope.scope is target.scope.scope:
                target.scope._instance_context = self
                yield None
                return

            for name in self.children:
                if name not in target.children:
                    raise DependencyError(message="Dependent target context does not have attribute").add(content=name).add(message="", object=target.scope)
                yield self[name], target[name]
        yield target_generator()
