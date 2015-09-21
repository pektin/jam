from contextlib import contextmanager, ExitStack

from ..errors import *

from .state import State
from .core import Context, Object, BoundObject, Scope, Type
from .util import inScope
from .links import Link

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

    # Hack for dependent functions
    _return_type = None

    def __init__(self, scope:Scope, name:str = None, tokens = None):
        super().__init__(name or "", tokens)
        self.scope = scope

        self.resolved_calls = dict()
        self.resolved_instance_calls = dict()
        self.compatible_types = set()
        self.switches = []

    @classmethod
    def switch(self, scope:Scope, targets:[Object], determiner:(lambda Object: bool)):
        out = DependentObject(scope)
        out.target_switch = targets
        out.target_switch_determiner = determiner
        return out

    @property
    def locked(self):
        return not inScope(self.scope, State.scope)

    def verify(self):
        if self.target: self.target.verify()

    # alias to the target if it exists
    def resolveValue(self):
        return self.target or self

    # Check whether an object matches the dependencies of this object
    @contextmanager
    def targetAt(self, target):
        with ExitStack() as stack:
            #TODO: Handle errors

            # Local checks
            if self.target_switch is not None:
                assert target.resolveValue() in self.target_switch

            if not self.checkLockedCompatibility(target):
                raise TypeError("TODO: Write this")

            # Set target
            previous_target = self.target
            self.target = target

            # Pass on dependency checks
            if self._context is not None:
                stack.enter_context(self.context.targetAt(target.context))

            if self._instance_context is not None:
                stack.enter_context(self.instance_context.targetAt(target.instance_context))

            if self.resolved_type is not None:
                stack.enter_context(self.resolved_type.targetAt(target.resolveType()))

            for call, obj in self.resolved_calls.items():
                stack.enter_context(obj.targetAt(target.resolveCall(call)))

            for call, obj in self.resolved_instance_calls.items():
                stack.enter_context(obj.targetAt(target.resolveInstanceCall(call)))

            for switch in self.switches:
                stack.enter_context(switch.resolveTarget())

            if self._return_type is not None:
                if not hasattr(target, "return_type"):
                    raise TypeError("TODO: Write this")
                stack.enter_context(self._return_type.targetAt(target.return_type))

            yield
            self.target = previous_target

    # Same as targetAt but for switches
    @contextmanager
    def resolveTarget(self):
        matches = []
        for possibility in self.target_switch:
            if self.target_switch_determiner(possibility):
                matches.append(possibility)

        if len(matches) < 1:
            raise InternalError("Target switch has impossible value")
        elif len(matches) > 1:
            raise TypeError("TODO: Write this")
        target = matches[0]

        previous_target = self.target
        self.target = target
        yield
        self.target = previous_target

    # Create and cache dependencies for standard object functionality

    @property
    def context(self):
        self._context = self._context or DependentContext(self)
        return self._context

    @property
    def instance_context(self):
        self._instance_context = self._instance_context or DependentContext(self)
        return self._instance_context

    def resolveType(self):
        self.resolved_type = self.resolved_type or DependentObject(self.scope)
        return self.resolved_type

    def resolveCall(self, call):
        return self.resolved_calls.setdefault(call, DependentObject(self.scope))

    # Hack!
    @property
    def return_type(self):
        self._return_type = self._return_type or DependentObject(self.scope)
        return self._return_type

    def resolveInstanceCall(self, call):
        return self.dependent_instance_calls.setdefault(call, DependentObject(self.scope))

    def checkCompatibility(self, other:Type):
        if self.target is not None: return self.target.checkCompatibility(other)
        if self.locked: return self.checkLockedCompatibility(other)
        if State.type_switching:
            self.compatible_type_switch = self.compatible_type_switch or []
            self.compatible_type_switch.append(other)
            State.type_switch_cleanups.append(self.typeSwitchCleanup)
        else:
            self.compatible_types.add(other)
        return True

    def checkLockedCompatibility(self, other:Type):
        for types in self.compatible_types:
            matches = []
            for type in types:
                if other.checkCompatibility(type):
                    matches.append(type)

            if len(matches) != 1:
                print(other, matches, self.compatible_types)
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
        super().__init__(value, tokens)
        self.dependencies = dependencies

    @contextmanager
    def target(self):
        with ExitStack() as stack:
            for object, target in self.dependencies:
                stack.enter_context(object.targetAt(target))
            yield

    def verify(self):
        with self.target():
            super().verify()

# The dependent context compliments the dependent object with the creation
# of dependencies for contexts.
class DependentContext(Context):
    dependent = True

    def __init__(self, scope:BoundObject):
        super().__init__(scope, [])

    def __contains__(self, name:str):
        if self.scope.locked: return super().__contains__(name)
        return True

    def __getitem__(self, name:str):
        if not self.scope.locked and name not in self.children:
            self.addChild(DependentObject(self.scope.scope, name))
        return self.children[name]

    def __setitem__(self, name:str, value:BoundObject):
        raise InternalError("Not Implemented.")

    @contextmanager
    def targetAt(self, target):
        with ExitStack() as stack:
            for name in self.children:
                if name not in target.children:
                    raise DependencyError("Dependent target context does not have attribute {}".format(name), target.scope.tokens)
            stack.enter_context(self[name].targetAt(target[name]))
            yield
