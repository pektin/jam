from contextlib import contextmanager

from .core import Object, Context, BoundObject, SoftScope, Scope
from .links import Link, BoundLink

class Closure(Scope):
    closed_context = None

    def __init__(self, name:str, tokens = None):
        Scope.__init__(self, name, tokens)

        self.closed_context = Context(self, [])

    def resolveIdentifier(self, name:str):
        found = BoundObject.resolveIdentifier(self, name)

        # Collect externally identifier, non-statics in the closed context
        for index, match in enumerate(found):
            if match is self: continue

            if not match.static:
                if match.name in self.closed_context:
                    found[index] = self.closed_context[match.name]
                else:
                    found[index] = match = ClosedLink(match)
                    self.closed_context.addChild(match)

        return found + SoftScope.resolveIdentifier(self, name)

class ClosedLink(BoundLink):
    def __str__(self):
        return "C({})".format(str(self.value))

class ClosedTarget(Link):
    targets = None

    def __init__(self, value:Object, targets:[(Object, Object)]):
        Link.__init__(self, value)

        self.targets = targets

    @contextmanager
    def target(self):
        oldValues = []

        for target, value in self.targets:
            target = target.resolveValue()
            oldValues.append(target.value)
            target.value = value

        yield

        for (target, new_value), old_value in zip(self.targets, oldValues):
            target.resolveValue().value = old_value
