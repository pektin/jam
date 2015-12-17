from abc import abstractmethod as abstract

from .. import lekvar
from ..errors import *

from .state import State
from .util import *
from . import bindings as llvm

# Abstract extensions

lekvar.BoundObject.llvm_value = None
lekvar.Function.llvm_return = None

# Extension abstract methods apparently don't work
#@patch
#@abstract
#def Object_emitValue(self, state:State) -> llvm.Value:
#    pass

#@patch
#@abstract
#def Type_emitType(self, state:State) -> llvm.Type:
#    pass

lekvar.Object.emitContext = blankEmit

#
# class Link
#

@patch
def Link_emit(self):
    return self.value.emit()

@patch
def Link_emitValue(self, type):
    return self.value.emitValue(type)

@patch
def Link_emitType(self):
    return self.value.emitType()

@patch
def Link_emitAssignment(self):
    return self.value.emitAssignment()

@patch
def Link_emitContext(self):
    return self.value.emitContext()

#
# class Attribute
#

@patch
def Attribute_emitValue(self, type):
    with State.selfScope(self.parent.emitAssignment()):
        return self.value.emitValue(type)

@patch
def Attribute_emitContext(self):
    return self.parent.emitAssignment()

@patch
def Attribute_emitAssignment(self):
    with State.selfScope(self.parent.emitAssignment()):
        return self.value.emitAssignment()

#
# class Literal
#

@patch
def Literal_emitValue(self, type):
    struct_type = self.type.emitType()

    if isinstance(self.data, str):
        data = State.builder.globalString(self.data, "")
    elif isinstance(self.data, bool):
        data = llvm.Value.constInt(llvm.Int.new(1), self.data, False)
    elif isinstance(self.data, int):
        data = llvm.Value.constInt(llvm.Int.new(64), self.data, False)
    elif isinstance(self.data, float):
        data = llvm.Value.constFloat(llvm.Float.double(), self.data)
    else:
        raise InternalError("Not Implemented")

    return llvm.Value.constStruct(struct_type, [data])

@patch
def Literal_emitAssignment(self):
    return State.pointer(self.emitValue(None))

#
# class Variable
#

lekvar.Variable.llvm_context_index = -1

@patch
def Variable_emit(self):
    if self.llvm_value is not None or self.llvm_context_index >= 0: return

    type = self.type.emitType()
    name = resolveName(self)
    if self.bound_context.scope.static:
        self.llvm_value = State.module.addVariable(type, name)
        self.llvm_value.initializer = llvm.Value.undef(type)
    else:
        self.llvm_value = State.alloca(type, name)

@patch
def Variable_emitValue(self, type):
    self.emit()

    return State.builder.load(self.emitAssignment(), "")

@patch
def Variable_emitAssignment(self):
    self.emit()

    if self.llvm_value is not None:
        return self.llvm_value

    return State.builder.structGEP(State.self, self.llvm_context_index, "")

@patch
def Variable_emitContext(self):
    return self.emitAssignment()

#
# class Assignment
#

@patch
def Assignment_emitValue(self, type):
    value = self.value.emitValue(self.assigned.resolveType())

    assigned = self.assigned.emitAssignment()
    State.builder.store(value, assigned)

#
# class Module
#

@patch
def Module_emit(self):
    if self.llvm_value is not None: return
    self.llvm_value = State.main

    State.addMainInstructions(self.main)

    for child in self.context:
        child.emit()

@patch
def Module_emitValue(self):
    raise InternalError("Not Implemented") #TODO: Implement Method values

#
# class Call
#

@patch
def Call_emitValue(self, type):
    with State.selfScope(self.called):
        called = self.function.emitValue(self.function_type)

    # Only use the function's context if it is static
    bound_value = None if self.called.resolveValue().static else self.called.emitContext()
    with State.selfScope(bound_value):
        context = self.function.emitContext()

    if context is not None:
        arguments = [State.builder.cast(context, llvm.Type.void_p(), "")]
    else:
        arguments = []

    arguments += [value.emitValue(None) for value in self.values]

    # Get the llvm function type
    return State.builder.call(called, arguments, "")

@patch
def Call_emitAssignment(self):
    return State.pointer(self.emitValue(None))

#
# class Return
#

@patch
def Return_emitValue(self, type):
    exit = self.function.llvm_value.getLastBlock()

    if self.value is not None:
        value = self.value.emitValue(None)
        State.builder.store(value, self.function.llvm_return)

    return State.builder.br(exit)

#
# class Context
#

lekvar.Context.llvm_type = None

@patch
def Context_emitType(self):
    if self.llvm_type is not None: return self.llvm_type

    types = []
    for index, child in self.children.items():
        child.llvm_context_index = index
        child_type = child.resolveType().emitType()
        types.append(llvm.Pointer.new(child_type, 0))

    if len(types) == 0:
        types = [llvm.Pointer.void_p()]

    self.llvm_type = llvm.Struct.newAnonym(types, False)

    return self.llvm_type

#
# class DependentObject
#

@patch
def DependentObject_emit(self):
    assert self.target is not None
    self.target.emit()

@patch
def DependentObject_emitValue(self, type):
    assert self.target is not None
    return self.target.emitValue(None)

@patch
def DependentObject_emitType(self):
    assert self.target is not None
    return self.target.emitType()

@patch
def DependentObject_emitContext(self):
    assert self.target is not None
    return self.target.emitContext()

#
# class DependentTarget
#

lekvar.DependentTarget.emitted = False

@patch
def DependentTarget_checkEmission(self):
    if not self.emitted:
        self.value.resetEmission()
        self.emitted = True

@patch
def DependentTarget_emit(self):
    self.checkEmission()
    with self.target():
        self.value.emit()

@patch
def DependentTarget_emitValue(self, type):
    self.checkEmission()
    with self.target():
        return self.value.emitValue(type)

#
# class Function
#

lekvar.Function.llvm_closure_type = None
lekvar.Function.llvm_context = None

@patch
def Function_resetEmission(self):
    self.llvm_value = None
    self.llvm_closure_type = None

@patch
def Function_emit(self):
    if self.llvm_value is not None: return

    self.llvm_closure_type = self.closed_context.emitType()

    name = resolveName(self)
    func_type = self.resolveType().emitType(self.llvm_closure_type is not None)
    self.llvm_value = State.module.addFunction(name, func_type)

    entry = self.llvm_value.appendBlock("entry")
    exit = self.llvm_value.appendBlock("exit")

    with State.blockScope(entry):

        for child in self.local_context:
            child.emit()

        # Only emit br if it hasn't already
        if not self.emitBody():
            State.builder.br(exit)

    with State.blockScope(exit):
        self.emitReturn()

@patch
def Function_emitBody(self):
    self.emitEntry()

    #context = State.builder.load(self.llvm_context, "")
    self_value = State.builder.structGEP(self.llvm_context, 0, "")
    self_value = State.builder.load(self_value, "")
    with State.selfScope(self_value):

        # Allocate Arguments
        for index, arg in enumerate(self.arguments):
            val = self.llvm_value.getParam(index + 1)
            arg.llvm_value = State.builder.alloca(arg.type.emitType(), resolveName(arg))
            State.builder.store(val, arg.llvm_value)

        self.emitPostContext()

        return State.emitInstructions(self.instructions)

@patch
def Function_emitEntry(self):
    #self.llvm_context = State.builder.alloca(self.llvm_closure_type, "context")
    self.llvm_context = State.builder.cast(self.llvm_value.getParam(0), llvm.Pointer.new(self.llvm_closure_type, 0), "")
    #State.builder.store(context, self.llvm_context)

@patch
def Function_emitPostContext(self):
    # Allocate Return Variable
    if self.type.return_type is not None:
        self.llvm_return = State.builder.alloca(self.type.return_type.emitType(), "return")

@patch
def Function_emitReturn(self):
    if self.llvm_return is not None:
        val = State.builder.load(self.llvm_return, "")
        State.builder.ret(val)
    else:
        State.builder.retVoid()

@patch
def Function_emitValue(self, type):
    self.emit()
    return self.llvm_value

@patch
def Function_emitContext(self):
    if State.self is not None and len(self.closed_context) > 0:
        context = State.alloca(self.llvm_closure_type, "")
        self_ptr = State.builder.structGEP(context, 0, "")
        State.builder.store(State.self, self_ptr)
        return context
    return llvm.Value.null(llvm.Pointer.new(self.llvm_closure_type, 0))

#
# Contructor
#

@patch
def Constructor_emitEntry(self):
    self.llvm_context = State.builder.alloca(self.llvm_closure_type, "")

    #context = State.builder.load(self.llvm_context, "")
    self_var = State.builder.structGEP(self.llvm_context, 0, "")
    self_val = State.builder.alloca(self.bound_context.scope.bound_context.scope.emitType(), "self")

    State.builder.store(self_val, self_var)

@patch
def Constructor_emitPostContext(self):
    pass

@patch
def Constructor_emitReturn(self):
    context = State.builder.structGEP(self.llvm_context, 0, "")
    value = State.builder.load(context, "")
    value = State.builder.load(value, "")
    State.builder.ret(value)

@patch
def Constructor_emitContext(self):
    with State.selfScope(None):
        return lekvar.Function.emitContext(self)

#
# class FunctionType
#

@patch
def FunctionType_emitType(self, has_context = True):
    if has_context:
        arguments = [llvm.Type.void_p()]
    else:
        arguments = []

    arguments += [type.emitType() for type in self.arguments]

    if self.return_type is not None:
        return_type = self.return_type.emitType()
    else:
        return_type = llvm.Type.void()
    return llvm.Function.new(return_type, arguments, False)

#
# class ExternalFunction
#

@patch
def ExternalFunction_emit(self):
    if self.llvm_value is not None: return

    name = resolveName(self)
    func_type = self.type.emitType(False)
    self.llvm_value = State.module.addFunction(name, func_type)

@patch
def ExternalFunction_emitValue(self, type):
    self.emit()
    return self.llvm_value

@patch
def ExternalFunction_emitContext(self):
    return None

#
# class Method
#

@patch
def Method_emit(self):
    for overload in self.overload_context:
        overload.emit()

@patch
def Method_emitValue(self, type):
    if type is None:
        type = self.resolveType()

    values = []
    overloads = list(self.overload_context)
    for overload_type in type.overload_types:
        for index, overload in enumerate(overloads):
            if overload.resolveType().checkCompatibility(overload_type):
                values.append(overload.emitValue(overload_type))
                overloads.pop(index)
                break

    return llvm.Value.constStruct(type.emitType(), values)

#
# class MethodType
#

lekvar.MethodType.llvm_type = None

@patch
def MethodType_emitType(self):
    if self.llvm_type is None:
        fn_types = [llvm.Pointer.new(type.emitType(), 0) for type in self.overload_types]
        self.llvm_type = llvm.Struct.newAnonym(fn_types, False)
    return self.llvm_type

#
# class MethodInstance
#

@patch
def MethodInstance_emit(self):
    pass

@patch
def MethodInstance_emitValue(self, type):
    self.emit()

    return State.builder.load(self.emitAssignment(), "")

@patch
def MethodInstance_emitAssignment(self):
    self.emit()

    value = State.self.emitAssignment()
    return State.builder.structGEP(value, self.target, "")

@patch
def MethodInstance_emitContext(self):
    return llvm.Value.null(llvm.Type.void_p())

#
# class Class
#

lekvar.Class.llvm_type = None

@patch
def Class_emit(self):
    if self.constructor is not None:
        self.constructor.emit()

    for child in self.instance_context:
        child.emit()

@patch
def Class_emitType(self):
    if self.llvm_type is None:
        var_types = []

        for child in self.instance_context:
            if isinstance(child, lekvar.Variable):
                child.llvm_context_index = len(var_types)
                var_types.append(child.type.emitType())

        self.llvm_type = llvm.Struct.newAnonym(var_types, False)

    return self.llvm_type

#
# class Loop
#

lekvar.Loop.after = None

@patch
def Loop_emitValue(self, type):
    # Grab the last block
    last_block = self.function.llvm_value.getLastBlock()
    # Create blocks
    loop_block = last_block.insertBlock("loop")
    self.after = last_block.insertBlock("after")

    # Reposition builder
    State.builder.br(loop_block)
    State.builder.positionAtEnd(loop_block)

    # Only loop if we don't return
    if not State.emitInstructions(self.instructions):
        # Loop
        # Rely on break to end the loop
        State.builder.br(loop_block)

    # Move the after block before the last block
    self.after.moveBefore(last_block)
    State.builder.positionAtEnd(self.after)

#
# class Break
#

@patch
def Break_emitValue(self, type):
    return State.builder.br(self.loop.after)

#
# class Branch
#

@patch
def Branch_emitValue(self, type):
    self.emit()

@patch
def Branch_emit(self, block = None):
    # Grab the last block
    last_block = self.function.llvm_value.getLastBlock()
    # Create blocks
    next_block = last_block.insertBlock("next")

    if self.condition is not None:
        block = next_block.insertBlock("branch")

        condition_value = self.condition.emitValue(None) # bool
        condition = State.builder.extractValue(condition_value, 0, "")
        State.builder.condBr(condition, block, next_block)

    State.builder.positionAtEnd(next_block)
    if self.next_branch is not None:
        after_block = self.next_branch.emit(next_block)
    else:
        after_block = next_block

    State.builder.positionAtEnd(block)
    if not State.emitInstructions(self.instructions):
        # Only br to after if we don't return
        State.builder.br(after_block)

    State.builder.positionAtEnd(after_block)
    return after_block
