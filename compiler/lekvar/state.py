import logging
from contextlib import contextmanager

# Python predefines
Module = None
BoundObject = None

# classproperty, because classmethod and property don't combine
class classproperty:
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, _, owner):
        return self.getter(owner)

# The global state for the verifier
class State:
    builtins = None
    logger = None
    scope_stack = None

    @classmethod
    def init(cls, builtins:Module, logger:logging.Logger):
        cls.builtins = builtins
        cls.logger = logger
        cls.scope_stack = []

    @classproperty
    def scope(cls):
        # Get the first element from the back that isn't soft
        for scope in reversed(cls.scope_stack):
            if not scope[1]:
                return scope[0]

    @classproperty
    def soft_scope(cls):
        return cls.scope_stack[-1]

    @classmethod
    def getSoftScope(cls, condition):
        for scope in reversed(cls.scope_stack):
            if scope[1]:
                if condition(scope[0]):
                    return scope[0]
            else:
                break

        return None

    @classmethod
    @contextmanager
    def scoped(cls, scope:BoundObject, soft = False):
        cls.scope_stack.append((scope, soft))
        yield
        cls.scope_stack.pop()
