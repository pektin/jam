from itertools import cycle
from contextlib import ExitStack

from .. import lekvar
from ..errors import InternalError

from .util import *
from .state import State
from . import builtins

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
# class Type
#

@patch
def Type_evalSize(self):
    raise InternalError("Not Implemented")

@patch
def Type_evalNewValue(self):
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

@patch
def Link_evalSize(self):
    return self.value.evalSize()

@patch
def Link_evalNewValue(self):
    return self.value.evalNewValue()

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
# class ClosedTarget
#

@patch
def ClosedTarget_eval(self):
    with self.target():
        result = self.value.eval()

        if result == self.value:
            return self
        return result

@patch
def ClosedTarget_evalContext(self):
    with self.target():
        return self.value.evalContext()

@patch
def ClosedTarget_evalCall(self, values):
    with self.target():
        return self.value.evalCall(values)

@patch
def ClosedTarget_evalAssign(self, value):
    with self.target():
        self.value.evalAssign(value)

@patch
def ClosedTarget_evalNewValue(self):
    with self.target():
        return self.value.evalNewValue()

#
# class Reference
#

@patch
def Reference_eval(self):
    return self.value.eval()

@patch
def Reference_evalContext(self):
    return self.value.evalContext()

@patch
def Reference_evalCall(self, values):
    return self.value.evalCall(values)

@patch
def Reference_evalAssign(self, value):
    self.value.evalAssign(value)

@patch
def Reference_evalSize(self):
    return builtins.PTR_SIZE

#
# class Module
#

lekvar.Module.evaled = False

@patch
def Module_eval(self):
    if self.evaled: return self
    self.evaled = True

    for instr in self.main:
        instr.eval()

    for obj in self.context:
        obj.eval()

    return self

#
# class Variable
#

@patch
def Variable_eval(self):
    if isinstance(self.parent, lekvar.Class):
        assert State.self is not None

        if not isinstance(State.self, lekvar.Literal) or not isinstance(State.self.data, dict):
            return State.self
        return State.self.data[self.name]

    if self.value is not None:
        return self.value
    return self

@patch
def Variable_evalContext(self):
    return self.eval()

@patch
def Variable_evalAssign(self, value):
    if isinstance(self.parent, lekvar.Class):
        assert State.self is not None
        assert isinstance(State.self, lekvar.Literal)

        State.self.data[self.name] = value
    else:
        self.value = value

@patch
def Variable_evalSize(self):
    return self.value.evalSize()

@patch
def Variable_evalNewValue(self):
    return self.value.evalNewValue()

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

@patch
def Method_evalCall(self, values):
    call = lekvar.FunctionType([value.resolveType() for value in values])
    call.verify()
    function = self.resolveCall(call)

    return function.evalCall(values)

#
# class MethodType
#

@patch
def MethodType_evalNewValue(self):
    return lekvar.Literal({}, self)

#
# class MethodInstance
#

@patch
def MethodInstance_eval(self):
    return State.self

@patch
def MethodInstance_evalCall(self, values):
    method = State.self

    call = lekvar.FunctionType([value.resolveType() for value in values])
    function = method.resolveCall(call)

    return function.evalCall(values)

#
# class Function
#

lekvar.Function.eval_returning = None
lekvar.Function.eval_returned = None

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
    self.eval_returned = False
    self.eval_returning = None

    previous_values = [arg.resolveValue().value for arg in self.arguments]
    for arg, val in zip(self.arguments, values):
        arg.evalAssign(val)

    for instr in self.instructions:
        instr.eval()

        if self.eval_returned:
            break

    for arg, val in zip(self.arguments, previous_values):
        arg.evalAssign(val)

    returning = self.eval_returning
    self.eval_returned = False
    self.eval_returning = None

    return returning

#
# class FunctionInstance
#

@patch
def FunctionInstance_eval(self):
    return self

@patch
def FunctionInstance_evalCall(self, values):
    return State.self.evalCall(values)

#
# class ExternalFunction
#

@patch
def ExternalFunction_eval(self):
    return self

@patch
def ExternalFunction_evalContext(self):
    return None

#
# class Class
#

@patch
def Class_eval(self):
    targets = [(value, value.eval()) for value in self.closed_context]

    if len(targets) == 0:
        return self
    return lekvar.ClosedTarget(self, targets)

@patch
def Class_evalCall(self, values):
    return self.constructor.evalCall(values)

@patch
def Class_evalContext(self):
    return None

@patch
def Class_evalSize(self):
    variables = [value for value in self.instance_context if isinstance(value, lekvar.Variable)]
    print(self, variables)
    sizes = [value.resolveType().evalSize() for value in variables]

    return sum(sizes)

@patch
def Class_evalNewValue(self):
    values = {}

    for value in self.instance_context:
        if not isinstance(value, lekvar.Variable):
            continue

        values[value.name] = value.resolveType().evalNewValue()

    return lekvar.Literal(values, self)

#
# class Constructor
#

@patch
def Constructor_evalCall(self, values):
    self_value = self.constructing.evalNewValue()

    with State.selfScope(self_value):
        lekvar.Function.evalCall(self, values)

    return self_value

#
# class ForwardTarget
#

@patch
def ForwardTarget_eval(self):
    with self.target():
        result = self.value.eval()

    if result is self.value:
        return self
    return result

@patch
def ForwardTarget_evalContext(self):
    raise InternalError("Not Implemented")

@patch
def ForwardTarget_evalCall(self, values):
    with self.target():
        return self.value.evalCall(values)

@patch
def ForwardTarget_evalAssign(self, value):
    raise InternalError("Not Implemented")

@patch
def ForwardTarget_evalNewValue(self):
    with self.target():
        return self.value.evalNewValue()

#
# class ForwardObject
#

@patch
def ForwardObject_eval(self):
    assert self.target is not None
    value = self.target.eval()
    if value is self.target:
        return self
    return value

@patch
def ForwardObject_evalContext(self):
    return self.target.evalContext()

@patch
def ForwardObject_evalCall(self, values):
    return self.target.evalCall(values)

@patch
def ForwardObject_evalAssign(self, value):
    self.target.evalAssign(value)

@patch
def ForwardObject_evalSize(self):
    return self.target.evalSize()

@patch
def ForwardObject_evalNewValue(self):
    return self.target.evalNewValue()

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
    with State.selfScope(self.called.eval()):
        called = self.function.eval()

    # Hack, for now
    scope = ExitStack()
    if isinstance(self.function, lekvar.ForwardTarget):
        scope = self.function.target()

    with scope:
        values = [value.eval() for value in self.values]

        context = self.called.evalContext()
        with State.selfScope(context):
            return called.evalCall(values)

@patch
def Call_evalContext(self):
    return self.called.eval()

#
# class Return
#

@patch
def Return_eval(self):
    if self.value is not None:
        self.function.eval_returning = self.value.eval()

    self.function.eval_returned = True
    return None

#
# class Branch
#

@patch
def Branch_eval(self):
    if self.condition is not None:
        value = self.condition.eval()
        assert isinstance(value, lekvar.Literal)

        bool_value = value.data
        if isinstance(value.data, dict):
            bool_value = value.data["value"].data

        if bool_value is False:
            if self.next_branch is not None:
                self.next_branch.eval()
            return

    for instr in self.instructions:
        instr.eval()

#
# class Loop
#

lekvar.Loop.breaking = False

@patch
def Loop_eval(self):
    self.breaking = False

    for instr in cycle(self.instructions):
        instr.eval()

        if self.breaking: break

#
# class Break
#

@patch
def Break_eval(self):
    self.loop.breaking = True

#
# class SizeOf
#

@patch
def SizeOf_evalCall(self, values):
    assert len(values) == 1
    value = values[0]

    return lekvar.Literal(value.evalSize(), self.type.return_type)

#
# class VoidType
#

@patch
def VoidType_eval(self):
    return

@patch
def VoidType_evalNewValue(self):
    return lekvar.Literal(0, self)
