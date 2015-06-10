import logging
from contextlib import contextmanager

from ..errors import *

from .state import State
from .core import Object, BoundObject, Type

# Python predefines
Module = None

def checkCompatibility(type1:Type, type2:Type):
    if type1.checkCompatibility(type2):
        return True
    elif type2.checkCompatibility(type1):
        return True
    return False

# Resolves a reference inside of a given scope.
def resolveReference(reference:str):
    # Collect all objects with a name matching reference up the tree of scopes
    found = []

    scope = State.scope
    while True:
        context = scope.local_context

        if context is not None and reference in context:
            found.append(context[reference])

        # Go to builtins once the top of the tree is reached, otherwise move up
        if scope is State.builtins:
            break
        else:
            scope = scope.bound_context.scope if (scope.bound_context is not None) else State.builtins

    # Only a single found object is valid
    if len(found) < 1:
        raise MissingReferenceError("No reference to {}".format(reference))
    elif len(found) > 1:
        raise AmbiguityError("Ambiguous reference to {}".format(reference))

    return found[0]

# Resolve a attribute of a given object
def resolveAttribute(object:Object, reference:str):
    context = object.context

    if context is not None and reference in context:
        return context[reference]

    raise MissingReferenceError("{} does not have an attribute {}".format(object, reference))

# More general copy function which handles None
def copy(obj):
    return obj.copy() if obj else None
