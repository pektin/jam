from . import bindings as llvm

from ..backend.util import *

# Emit a value targeting a specific type
def emitValue(value, type):
    return value.resolveType().resolveValue().emitInstanceValue(value, type)

# Emit an assigneable value targeting a specific type
def emitAssignment(value, type):
    return value.resolveType().resolveValue().emitInstanceAssignment(value, type)

# Emits a set of instructions and returns whether or not the set has a br instruction
# to eliminate some dead code
def emitInstructions(instructions):
    for instruction in instructions:
        value = instruction.emitValue(None)

        if value is not None and value.opcode == llvm.Opcode.Br:
            return True
    return False

def newStruct(builder, type, attributes):
    undefs = [llvm.Value.undef(attr.type) for attr in attributes]
    struct = llvm.Value.constStruct(type, undefs)

    for index, attr in enumerate(attributes):
        struct = builder.insertValue(struct, attr, index, "")

    return struct
