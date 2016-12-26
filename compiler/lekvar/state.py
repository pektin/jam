import logging
from io import IOBase
from contextlib import contextmanager

from .. errors import *

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
    source = None
    sources = None
    builtins = None
    logger = None

    scope_stack = None

    # Other global state
    type_switching = False

    @classmethod
    def init(cls, logger:logging.Logger):
        cls.logger = logger
        cls.scope_stack = []
        cls.sources = None

    @classproperty
    def scope(cls):
        for scope, soft in reversed(cls.scope_stack):
            if not soft:
                return scope

    @classproperty
    def soft_scope(cls):
        scope, soft = cls.scope_stack[-1]
        return scope

    @classmethod
    def getSoftScope(cls, condition):
        for scope, soft in reversed(cls.scope_stack):
            if soft:
                if condition(scope):
                    return scope
            else:
                break

    @classmethod
    @contextmanager
    def scoped(cls, scope:BoundObject, soft = False):
        state = (scope, soft)
        cls.scope_stack.append(state)
        yield
        cls.scope_stack.pop()

    @classmethod
    @contextmanager
    def type_switch(cls):
        cls.type_switch_cleanups = []
        cls.type_switching = True
        yield
        cls.type_switching = False
        for fn in cls.type_switch_cleanups: fn()

    @classmethod
    @contextmanager
    def ioSource(cls, source:IOBase):
        previous_source = cls.source
        cls.source = source
        yield source
        cls.source = previous_source
