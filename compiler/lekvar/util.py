import logging
from contextlib import contextmanager

from ..errors import *

from .state import State
from .core import Object, BoundObject, Scope, Type

# Python predefines
Module = None

def checkCompatibility(type1:Type, type2:Type):
    if type1.checkCompatibility(type2):
        return True
    return type2.checkCompatibility(type1)

# Resolve a attribute of a given object
def resolveAttribute(object:Object, reference:str):
    context = object.context

    if context is not None and reference in context:
        return context[reference]
    raise MissingReferenceError(object=object).add(message="does not have an attribute")

# Check whether a object is within a scope
def inScope(object:BoundObject, scope:Scope):
    while scope is not None:
        if object == scope:
            return True
        scope = scope.parent
    return False
