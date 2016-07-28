from contextlib import ExitStack

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

@patch
def Object_evalContext(self):
    raise InternalError("Not Implemented")

@patch
def Object_evalCall(self, values):
    raise InternalError("Not Implemented")

@patch
def Object_evalAssign(self, value):
    raise InternalError("Not Implemented")

#
# class Link
#

@patch
def Link_eval(self):
    return self.value.eval()

@patch
def Link_evalContext(self):
    return self.value.evalContext()

@patch
def Link_evalCall(self, values):
    return self.value.evalCall(values)

@patch
def Link_evalAssign(self, value):
    self.value.evalAssign(value)

#
# class Attribute
#

@patch
def Attribute_eval(self):
    with State.selfScope(self.object.eval()):
        return self.value.eval()

@patch
def Attribute_evalContext(self):
    return self.object.eval()

@patch
def Attribute_evalCall(self, values):
    with State.selfScope(self.object.eval()):
        return self.value.evalCall(values)

@patch
def Attribute_evalAssign(self, value):
    with State.selfScope(self.object.eval()):
        self.value.evalAssign(value)

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
        assert isinstance(State.self, lekvar.Literal)

        if not isinstance(State.self.data, dict):
            return State.self
        return State.self.data[self.name]

    assert self.eval_value is not None
    return self.eval_value

@patch
def Variable_evalContext(self):
    return None

@patch
def Variable_evalAssign(self, value):
    if isinstance(self.parent, lekvar.Class):
        assert State.self is not None
        assert isinstance(State.self, lekvar.Literal)

        State.self.data[self.name] = value
    else:
        self.eval_value = value

#
# class Assignment
#

@patch
def Assignment_eval(self):
    self.assigned.evalAssign(self.value.eval())

#
# class Method
#

@patch
def Method_eval(self):
    return self

@patch
def Method_evalContext(self):
    return None

#
# class Function
#

lekvar.Function.eval_returning = None

@patch
def Function_eval(self):
    return self

@patch
def Function_evalContext(self):
    #TODO: Implement closures
    assert len(self.closed_context) == 0

    return None

@patch
def Function_evalCall(self, values):
    self.eval_returning = None

    for arg, val in zip(self.arguments, values):
        arg.evalAssign(val)

    for instr in self.instructions:
        instr.eval()

    return self.eval_returning

#
# class Class
#

@patch
def Class_eval(self):
    return self

@patch
def Class_evalContext(self):
    return None

#
# class Constructor
#

@patch
def Constructor_evalCall(self, values):
    self_value = lekvar.Literal({}, self.constructing)

    with State.selfScope(self_value):
        lekvar.Function.evalCall(self, values)

    return self_value

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

    with State.selfScope(self.called.evalContext()):
        return self.function.evalCall(values)

#
# class Return
#

@patch
def Return_eval(self):
    self.function.eval_returning = self.value.eval()
    return None

#
# class Branch
#

@patch
def Branch_eval(self):
    if self.condition is not None:
        value = self.condition.eval()
        assert isinstance(value, lekvar.Literal)

        print(value)
        if value.data is False:
            if self.next_branch is not None:
                self.next_branch.eval()
            return

    for instr in self.instructions:
        instr.eval()
