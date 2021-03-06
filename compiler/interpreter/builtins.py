import sys
import math
import logging
from functools import partial

from .util import *
from .state import State
from .. import lekvar

def builtins(logger = logging.getLogger()):
    global printf
    printf = None

    string = PyType("String", str)
    size = PyType("Int64", int)
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
    void = lekvar.VoidType("Void")

    builtin_objects = [string, bool_, void] + ints + floats

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
        (floats, "floatGreaterThan", (lambda a, b: a > b), bool_),
        (floats, "floatGreaterOrEqualTo", (lambda a, b: a >= b), bool_),
        (floats, "floatSmallerThan", (lambda a, b: a < b), bool_),
        (floats, "floatSmallerOrEqualTo", (lambda a, b: a <= b), bool_),

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

    # int -> float conversions
    for int_t in ints:
        for float_t in floats:
            name = int_t.name + "To" + float_t.name
            function = PyFunction(name, [int_t], float_t, lambda i: float(i))
            builtin_objects.append(function)

    # float -> int conversions
    for float_t in floats:
        for int_t in ints:
            name = float_t.name + "To" + int_t.name
            function = PyFunction(name, [float_t], int_t, lambda f: int(f))
            builtin_objects.append(function)

    overloads = []
    for type in ints + floats + [string]:
        def py_func(v, type=type):
            State.print(PRINT_MAP[type.name] % v)

        function = PyFunction("", [type], None, py_func)
        overloads.append(function)

    print_ = lekvar.Method("print", overloads)
    builtin_objects.append(print_)

    builtin_objects.append(PyFunction("alloc", [size], void, lambda s: PyPointer(s)))
    builtin_objects.append(PyFunction("free", [void], None, lambda ptr: None))
    builtin_objects.append(PyFunction("realloc", [void, size], void, lambda ptr, s: ptr.resize(s)))
    builtin_objects.append(PyFunction("ptrOffset", [void, size], void, lambda ptr, s: ptr.offset(s)))

    module = lekvar.Module("_builtins", builtin_objects)
    module.verify()
    return module

class PyPointer:
    def __init__(self, size = 0):
        self.hand = 0
        self.value = [None] * size

    def get(self):
        return self.value[self.hand]

    def set(self, value):
        self.value[self.hand] = value

    def offset(self, amount):
        ptr = PyPointer()
        ptr.hand = self.hand + amount
        ptr.value = self.value
        return ptr

    def resize(self, new_size):
        self.value += [None] * (new_size - len(self.value))

    def __repr__(self):
        if len(self.value) == 0:
            return "PyPtr(None)"
        return "PyPtr({}, {})".format(self.get(), self.value)

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

PTR_SIZE = math.ceil(math.log(sys.maxsize, 2) / 8) # Hack for
SIZE_MAP = {
    "String": PTR_SIZE,

    "Bool": 1,

    "Int8": 1,
    "Int16": 2,
    "Int32": 4,
    "Int64": 8,
    "Int128": 16,

    "Float16": 2,
    "Float32": 4,
    "Float64": 8,
}

class PyType(lekvar.Type, lekvar.BoundObject):
    py_type = None

    def __init__(self, name:str, py_type):
        lekvar.BoundObject.__init__(self, name)
        self.py_type = py_type

    def verify(self):
        self._stats = lekvar.stats.ScopeStats(self.parent)
        self.stats.static = True
        self.stats.forward = False

    def resolveType(self):
        raise InternalError("PyTypes are typeless")

    @property
    def local_context(self):
        raise InternalError("PyTypes do not have a local context")

    def checkCompatibility(self, other:lekvar.Type, check_cache = None):
        other = other.resolveValue()

        if isinstance(other, PyType):
            if self.name == other.name:
                return True
        return False

    def eval(self):
        return None

    def evalSize(self):
        return SIZE_MAP[self.name]

    def evalNewValue(self):
        return lekvar.Literal(self.py_type(), self)

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
