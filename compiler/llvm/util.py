from .. import lekvar
from . import bindings as llvm

# Resolves the name of a scope, starting with a extraneous .
def resolveName(scope:lekvar.BoundObject):
    name = ""
    while scope.bound_context is not None:
        name = "." + scope.name + name
        scope = scope.bound_context.scope
    return "lekvar" + name

# A blank emission function. Can be used for anything
def blankEmit(self):
    return None
# A blank value emission function. requires type argument
def blankEmitValue(self, type):
    return None

# Create a reference counted type from a normal type
def referenceType(type):
    return llvm.Struct.newAnonym([llvm.Type.void_p(), type], False)

# Emit a value targeting a specific type
def emitValue(value, type):
    return value.resolveType().emitInstanceValue(value, type)

# Emit an assigneable value targeting a specific type
def emitAssignment(value, type):
    return value.resolveType().emitInstanceAssignment(value, type)

# Mokeypatch a function into a lekvar class
# The lekvar class is determined from the name of the function, which should be
# in the following format: <class-name>_<function-name>
def patch(fn):
    class_name, func_name = fn.__name__.split("_")
    class_ = getattr(lekvar, class_name)
    setattr(class_, func_name, fn)
