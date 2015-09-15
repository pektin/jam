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
    def init(cls, builtins:Module, logger:logging.Logger):
        cls.builtins = builtins
        cls.logger = logger
        cls.scope_stack = []
        cls.sources = None

    @classproperty
    def scope_state(cls):
        # Get the first element from the back that isn't soft
        for scope_state in reversed(cls.scope_stack):
            if not scope_state.soft:
                return scope_state
    @classproperty
    def scope(cls):
        return cls.scope_state.scope

    @classproperty
    def soft_scope_state(cls):
        return cls.scope_stack[-1]
    @classproperty
    def soft_scope(cls):
        return cls.soft_scope_state.scope

    @classmethod
    def getSoftScopeState(cls, condition):
        for scope_state in reversed(cls.scope_stack):
            if scope_state.soft:
                if condition(scope_state.scope):
                    return scope_state
            else:
                break
    @classmethod
    def getSoftScope(cls, condition):
        state = cls.getSoftScopeState(condition)
        return state.scope if state is not None else None

    @classmethod
    @contextmanager
    def scoped(cls, scope:BoundObject, soft = False, analys = False):
        scope_state = AnalysScopeState(scope) if analys else ScopeState(scope)
        scope_state.soft = soft

        cls.scope_stack.append(scope_state)
        yield scope_state
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
        yield
        cls.source = previous_source

class ScopeState:
    soft = False

    def __init__(self, scope:BoundObject):
        self.scope = scope

    def merge_or(self, other):
        out = self.copy()
        out.imerge_or(other)
        return out

    def merge_and(self, other):
        out = self.copy()
        out.imerge_and(other)
        return out

    def copy(self):
        return ScopeState(self.scope)

    def imerge_or(self, other):
        raise InternalError("Cannot merge default scope states")

    def imerge_and(self, other):
        raise InternalError("Cannot merge default scope states")

class AnalysScopeState(ScopeState):
    def __init__(self, scope:BoundObject):
        super().__init__(scope)
        self.definately_returns = False
        self.maybe_returns = False

    def copy(self):
        state = AnalysScopeState(self.scope)
        state.definately_returns = self.definately_returns
        state.maybe_returns = self.maybe_returns
        return state

    def imerge_or(self, other):
        self.definately_returns = self.definately_returns and other.definately_returns
        self.maybe_returns = self.definately_returns or other.definately_returns

    def imerge_and(self, other):
        self.definately_returns = self.definately_returns or other.definately_returns
        self.maybe_returns = self.definately_returns or other.definately_returns
