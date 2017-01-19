from ..backend.util import *

def evalValue(value, type):
    return value.resolveType().resolveValue().evalInstanceValue(value, type)
