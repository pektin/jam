from .. import lekvar

# Resolves the name of a scope
def resolveName(scope:lekvar.BoundObject):
    name = ""
    while scope.bound_context is not None:
        name = "." + scope.name + name
        scope = scope.parent
    return "lekvar" + name

# Mokeypatch a function into a lekvar class
# The lekvar class is determined from the name of the function, which should be
# in the following format: <class-name>_<function-name>
def patch(fn):
    class_name, func_name = fn.__name__.split("_")
    class_ = getattr(lekvar, class_name)
    setattr(class_, func_name, fn)
