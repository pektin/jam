from . import bindings as llvm

from ..backend.util import *

# Create a reference counted type from a normal type
def referenceType(type):
    return llvm.Struct.newAnonym([llvm.Type.void_p(), type], False)

# Emit a value targeting a specific type
def emitValue(value, type):
    return value.resolveType().resolveValue().emitInstanceValue(value, type)

# Emit an assigneable value targeting a specific type
def emitAssignment(value, type):
    return value.resolveType().resolveValue().emitInstanceAssignment(value, type)
