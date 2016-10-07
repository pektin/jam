import logging
from functools import partial

from .util import *
from .state import State
from .. import lekvar

def builtins(logger = logging.getLogger()):
    global printf
    printf = None

    string = PyType("String", str)
    ints = [
        PyType("Int8",   int),
        PyType("Int16",  int),
        PyType("Int32",  int),
        PyType("Int64",  int),
        PyType("Int128", int),
    ]
    floats = [
        PyType("Float16", float),
        PyType("Float32", float),
        PyType("Float64", float),
    ]
    bool_ = PyType("Bool", bool)

    builtin_objects = [string, bool_] + ints + floats

    # (the types the method applies to, the name, the instruction, additional arguments)
    methods = [
        (ints, "intAdd", int.__add__, None),
        (ints, "intSub", int.__sub__, None),
        (ints, "intMul", int.__mul__, None),
        (ints, "intDiv", int.__floordiv__, None),
        (ints, "intRem", int.__mod__, None),
        (ints, "intEqual", int.__eq__, bool_),
        (ints, "intUnequal", (lambda a, b: a != b), bool_),
        (ints, "intGreaterThan", (lambda a, b: a > b), bool_),
        (ints, "intGreaterOrEqualTo", (lambda a, b: a >= b), bool_),
        (ints, "intSmallerThan", (lambda a, b: a < b), bool_),
        (ints, "intSmallerOrEqualTo", (lambda a, b: a <= b), bool_),
        (floats, "floatAdd", float.__add__, None),
        (floats, "floatSub", float.__sub__, None),
        (floats, "floatMul", float.__mul__, None),
        (floats, "floatDiv", float.__truediv__, None),
        (floats, "floatRem", float.__mod__, None),
    ]

    for types, name, function, return_type in methods:

        functions = []
        for type in types:
            r_type = return_type if return_type else type

            functions.append(
                PyFunction("", [type, type], r_type, function)
            )
        builtin_objects.append(
            lekvar.Method(name, functions)
        )

    overloads = []
    for type in ints + floats + [string]:
        def py_func(v, type=type):
            State.print(PRINT_MAP[type.name] % v)

        function = PyFunction("", [type], None, py_func)
        overloads.append(function)

    puts = lekvar.Method("puts", overloads)
    builtin_objects.append(puts)

    return lekvar.Module("_builtins", builtin_objects)

PRINT_MAP = {
    "String": "%s",

    "Int8": "%hhd",
    "Int16": "%hd",
    "Int32": "%d",
    "Int64": "%ld",
    "Int128": "%lld",

    "Float16": "%hg",
    "Float32": "%g",
    "Float64": "%lg",
}

class PyType(lekvar.Type, lekvar.BoundObject):
    py_type = None

    def __init__(self, name:str, py_type):
        lekvar.BoundObject.__init__(self, name)
        self.py_type = py_type

    def verify(self):
        pass

    def resolveType(self):
        raise InternalError("PyTypes are typeless")

    @property
    def local_context(self):
        raise InternalError("PyTypes do not have a local context")

    def checkCompatibility(self, other:lekvar.Type):
        other = other.resolveValue()

        if isinstance(other, PyType):
            if self.name == other.name:
                return True
        return False

    def eval(self):
        return None

    def __repr__(self):
        return "{}<{}>".format(self.__class__.__name__, self.name)

class PyFunction(lekvar.ExternalFunction):
    py_func = None

    def __init__(self, name:str, arguments:[lekvar.Type], return_type:lekvar.Type, py_func):
        lekvar.ExternalFunction.__init__(self, name, name, arguments, return_type)
        self.py_func = py_func

    @property
    def local_context(self):
        raise InternalError("PyFunctions do not have a local context")

    def evalCall(self, values:[lekvar.Object]):
        assert all(isinstance(val, lekvar.Literal) for val in values)

        args = [val.data for val in values]
        result = self.py_func(*args)
        return lekvar.Literal(result, self.type.return_type)
