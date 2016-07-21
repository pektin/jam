from .. import lekvar
from ..errors import InternalError

from .util import *
from .state import State

#
# class Object
#

@patch
def Object_eval(self):
    raise InternalError("Not Implemented")

#
# class Link
#

@patch
def Link_eval(self):
    return self.value.eval()

@patch
def Link_evalCall(self, values):
    return self.value.evalCall(values)

#
# class Attribute
#

@patch
def Attribute_eval(self):
    with State.selfScope(self.object.eval()):
        return self.value.eval()

@patch
def Attribute_evalCall(self, values):
    with State.selfScope(self.object.eval()):
        return self.value.evalCall(values)

#
# class Module
#

@patch
def Module_eval(self):
    for instr in self.main:
        instr.eval()

    for obj in self.local_context:
        obj.eval()

    return self

#
# class Variable
#

lekvar.Variable.eval_value = None

@patch
def Variable_eval(self):
    if isinstance(self.parent, lekvar.Class):
        assert State.self is not None

        return State.self
    return self.eval_value

#
# class Method
#

@patch
def Method_eval(self):
    return self

#
# class Function
#

lekvar.Function.eval_returning = None

@patch
def Function_eval(self):
    return self

@patch
def Function_evalCall(self, values):
    self.eval_returning = None

    for arg, val in zip(self.arguments, values):
        arg.eval_value = val

    for instr in self.instructions:
        instr.eval()

    return self.eval_returning

#
# class Literal
#

@patch
def Literal_eval(self):
    return self

#
# class Call
#

@patch
def Call_eval(self):
    values = [value.eval() for value in self.values]

    return self.function.evalCall(values)

#
# class Return
#

@patch
def Return_eval(self):
    self.function.eval_returning = self.value.eval()

    return None
