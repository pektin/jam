from contextlib import contextmanager, ExitStack

from .core import Object, Context, BoundObject, SoftScope, Scope
from .links import Link, BoundLink, ContextLink

class Closure(Scope):
    closed_context = None

    def __init__(self, name:str, tokens = None):
        Scope.__init__(self, name, tokens)

        self.closed_context = Context(self, [])

    def resolveIdentifier(self, name:str, exclude = []):
        found = BoundObject.resolveIdentifier(self, name, exclude)

        # Collect externally identifier, non-statics in the closed context
        for index, match in enumerate(found):
            if match is self: continue

            match.verify()
            if not match.stats.static:
                if match.name in self.closed_context:
                    found[index] = self.closed_context[match.name]
                else:
                    found[index] = match = ClosedLink(match)
                    self.closed_context.addChild(match)

        return found + SoftScope.resolveIdentifier(self, name, exclude)

class ClosedLink(BoundLink):
    bound_context = None

    def __str__(self):
        return "C({})".format(str(self.value))

class ClosedTarget(Link):
    origin = None
    targets = None

    def __init__(self, value:Object, targets:[(Object, Object)], origin:Object = None):
        Link.__init__(self, value)

        self.targets = targets
        self.origin = origin or value

    @contextmanager
    def target(self):
        stack = ExitStack()

        for target, value in self.targets:
            stack.enter_context(target.resolveValue().targetValue(value))

        with stack:
            yield

    def retarget(self, value:Object):
        return ClosedTarget(value, self.targets, self.value)

    def resolveIdentifier(self, name:str):
        with self.target():
            return self.retarget(self.value.resolveIdentifier(name))

    def resolveCall(self, call):
        with self.target():
            return self.retarget(self.value.resolveCall(call))

    @property
    def context(self):
        return ClosedTargetContext(self.value.context, self)

    @property
    def instance_context(self):
        return ClosedTargetContext(self.value.instance_context, self)

    @property
    def return_type(self):
        return self.retarget(self.value.return_type)

    def resolveType(self):
        return self.retarget(self.value.resolveType())

    def checkCompatibility(self, other, check_cache = None):
        with self.target():
            return self.value.checkCompatibility(other, check_cache)

    def revCheckCompatibility(self, other, check_cache = None):
        with self.target():
            return self.value.revCheckCompatibility(other, check_cache)

    def __repr__(self):
        return "CT({}, {})".format(self.value, self.targets)

    def resolveValue(self):
        return self

class ClosedTargetContext(ContextLink):
    targeter = None

    def __init__(self, value, targeter):
        ContextLink.__init__(self, value)
        self.targeter = targeter

    def retarget(self, value):
        return self.targeter.retarget(value)

    def __getitem__(self, name:str):
        return self.retarget(ContextLink.__getitem__(self, name))

    def __iter__(self):
        for item in ContextLink.__iter__(self):
            yield self.retarget(item)

    def __repr__(self):
        return "CT({})".format(self.value)
