from abc import abstractmethod as abstract
from contextlib import ExitStack

from .. import lekvar
from ..errors import InternalError

from .state import State
from .util import *
from . import bindings as llvm

# Abstract extensions

lekvar.BoundObject.llvm_value = None

# Extension abstract methods apparently don't work

@patch
#@abstract
def Object_emitValue(self, type:lekvar.Type) -> llvm.Value:
    raise InternalError("Not Implemented")

@patch
#@abstract
def Object_emitAssignment(self, type:lekvar.Type) -> llvm.Value:
    return None

@patch
#@abstract
def Type_emitType(self) -> llvm.Type:
    raise InternalError("Not Implemented")

@patch
def Type_emitInstanceValue(self, value:lekvar.Object, type:lekvar.Type) -> llvm.Value:
    return value.emitValue(type)

@patch
def Type_emitInstanceAssignment(self, value:lekvar.Object, type:lekvar.Type) -> llvm.Value:
    return value.emitAssignment(type)

#
# class Link
#

@patch
def Link_resetEmission(self):
    self.value.resetEmission()

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
def Link_emitAssignment(self, type):
    return self.value.emitAssignment(type)

@patch
def Link_emitContext(self):
    return self.value.emitContext()

@patch
def Link_emitInstanceValue(self, value, type):
    return self.value.emitInstanceValue(value, type)

@patch
def Link_emitInstanceAssignment(self, value, type):
    return self.value.emitInstanceAssignment(value, type)

#
# class Attribute
#

@patch
def Attribute_emitValue(self, type):
    with State.selfScope(emitAssignment(self.object, None)):
        return emitValue(self.value, type)

@patch
def Attribute_emitContext(self):
    return emitAssignment(self.object, None)

@patch
def Attribute_emitAssignment(self, type):
    with State.selfScope(emitAssignment(self.object, None)):
        return self.value.emitAssignment(type)

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
def Literal_emitAssignment(self, type):
    return State.pointer(self.emitValue(None))

#
# class Variable
#

lekvar.Variable.llvm_context_index = -1
lekvar.Variable.llvm_self_index = -1

@patch
def Variable_resetEmission(self):
    self.llvm_value = None
    self.llvm_context_index = -1
    self.llvm_self_index = -1

@patch
def Variable_emit(self):
    if (self.llvm_value is not None or
        self.llvm_context_index >= 0 or
        self.llvm_self_index >= 0): return

    type = self.type.emitType()
    name = resolveName(self)
    if self.static:
        self.llvm_value = State.module.addVariable(type, name)
        self.llvm_value.initializer = llvm.Value.undef(type)
    else:
        self.llvm_value = State.alloca(type, name)

@patch
def Variable_emitValue(self, type):
    self.emit()

    return State.builder.load(self.emitAssignment(type), "")

@patch
def Variable_emitAssignment(self, type):
    self.emit()

    if self.llvm_value is not None:
        return self.llvm_value

    if self.llvm_self_index < 0:
        raise InternalError()

    assert State.self is not None
    return State.builder.structGEP(State.self, self.llvm_self_index, "")

@patch
def Variable_emitContext(self):
    return self.emitAssignment(None)

#
# class Assignment
#

@patch
def Assignment_emitValue(self, type):
    value = emitValue(self.value, self.assigned.resolveType())

    assigned = emitAssignment(self.assigned, self.value.resolveType())
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
    with State.selfScope(self.called.emitAssignment(type)):
        called = self.function.emitValue(self.function_type)

    bound_value = self.called.emitContext()
    with State.selfScope(bound_value):
        context = self.function.resolveValue().emitContext()

    if context is not None:
        arguments = [State.builder.cast(context, llvm.Type.void_p(), "")]
    else:
        arguments = []

    # Hack, for now
    scope = ExitStack()
    if isinstance(self.function, lekvar.DependentTarget):
        scope = self.function.target()

    with scope:
        argument_types = self.function.resolveValue().resolveType().resolveValue().arguments
        arguments += [emitValue(value, type) for value, type in zip(self.values, argument_types)]

    # Get the llvm function type
    return State.builder.call(called, arguments, "")

@patch
def Call_emitAssignment(self, type):
    return State.pointer(self.emitValue(None))

@patch
def Call_emitContext(self):
    return self.called.emitContext()

#
# class Return
#

@patch
def Return_emitValue(self, type):
    exit = self.function.llvm_value.getLastBlock()

    if self.value is not None:
        if self.function.type.return_type is None:
            self.value.emitValue(None)
        else:
            value = emitValue(self.value, self.function.type.return_type)
            State.builder.store(value, self.function.llvm_return)

    return State.builder.br(exit)

#
# class Context
#

lekvar.Context.llvm_type = None

@patch
def Context_emitType(self):
    if self.llvm_type is not None: return self.llvm_type

    index = 0
    types = []

    # specialcase for 'self'
    if "self" in self.children:
        self_value = self.children["self"]
        self_value.llvm_context_index = index
        index += 1
        self_type = self_value.resolveType().emitType()
        types.append(llvm.Pointer.new(self_type, 0))

    for child in self.children.values():
        if child.name == "self": continue

        child.llvm_context_index = index
        index += 1
        types.append(child.resolveType().emitType())

    if len(types) == 0:
        types = [llvm.Pointer.void_p()]

    self.llvm_type = llvm.Struct.newAnonym(types, False)

    return self.llvm_type

#
# class DependentObject
#

@patch
def DependentObject_emit(self):
    raise InternalError("Not Implemented")

@patch
def DependentObject_emitValue(self, type):
    assert self.target is not None
    return self.target.emitValue(type)

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
        return False
    return True

@patch
def DependentTarget_emit(self):
    raise InternalError("Not Implemented")

@patch
def DependentTarget_emitValue(self, type):
    if self.value.emitted_cache is None:
        self.value.emitted_cache = {}
    cache = self.value.emitted_cache

    with self.target():
        if type not in cache:
            assert not self.checkEmission()

            #TODO: Make this generic, currently specific for Function
            # Maybe turn the entire emitter into a sequenced collection of generators,
            # like dependent object targeting, which would also allow for multithreading
            assert isinstance(self.value, lekvar.Function)
            self.value.emitStatic()
            cache[type] = self.value.llvm_value
            self.value.emitBody()
        return cache[type]

#
# class ClosedLink
#

lekvar.ClosedLink.llvm_value = None

@patch
def ClosedLink_emitValue(self, type):
    return State.builder.load(self.emitAssignment(type), "")

@patch
def ClosedLink_emitAssignment(self, type):
    return self.llvm_value

@patch
def ClosedLink_emitLinkValue(self, type):
    return self.value.emitValue(type)

#
# class Function
#

lekvar.Function.llvm_return = None
lekvar.Function.llvm_context = None
lekvar.Function.llvm_closure_type = None
lekvar.Function.emitted_cache = None

@patch
def Function_resetEmission(self):
    self.llvm_value = None
    self.llvm_closure_type = None

    for child in self.local_context:
        child.resetEmission()

@patch
def Function_emit(self):
    if self.llvm_value is not None: return

    self.emitStatic()
    self.emitBody()

@patch
def Function_emitStatic(self):
    self.llvm_closure_type = self.closed_context.emitType()

    name = resolveName(self)
    func_type = self.resolveType().emitFunctionType(self.llvm_closure_type is not None)
    self.llvm_value = State.module.addFunction(name, func_type)

@patch
def Function_emitBody(self):
    entry = self.llvm_value.appendBlock("entry")
    exit = self.llvm_value.appendBlock("exit")

    with State.blockScope(entry):
        # Only emit br if it hasn't already
        if not self.emitInstructions():
            State.builder.br(exit)

        for child in self.local_context:
            child.emit()

    with State.blockScope(exit):
        self.emitReturn()

@patch
def Function_emitInstructions(self):
    self.emitEntry()

    # Exit stack that might contain a selfScope
    self_stack = ExitStack()
    if "self" in self.closed_context:
        index = self.closed_context["self"].llvm_context_index
        self_value = State.builder.structGEP(self.llvm_context, index, "")
        self_value = State.builder.load(self_value, "")
        self_stack.enter_context(State.selfScope(self_value))

    with self_stack:
        for object in self.closed_context:
            if object.name == "self": continue

            index = object.llvm_context_index
            object.llvm_value = State.builder.structGEP(self.llvm_context, index, "")

        # Allocate Arguments
        for index, arg in enumerate(self.arguments):
            val = self.llvm_value.getParam(index + 1)
            arg.llvm_value = State.builder.alloca(arg.resolveType().emitType(), resolveName(arg))
            State.builder.store(val, arg.llvm_value)

        self.emitPostContext()

        return State.emitInstructions(self.instructions)

@patch
def Function_emitEntry(self):
    context_param = self.llvm_value.getParam(0)
    context_type = llvm.Pointer.new(self.llvm_closure_type, 0)
    self.llvm_context = State.builder.cast(context_param, context_type, "context")

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
    if len(self.closed_context) > 0:
        context = State.alloca(self.llvm_closure_type, "")

        #TODO: Remove this special case
        if State.self is not None and "self" in self.closed_context:
            index = self.closed_context["self"].llvm_context_index
            self_ptr = State.builder.structGEP(context, index, "")
            State.builder.store(State.self, self_ptr)

        for object in self.closed_context:
            if object.name == "self": continue

            obj_ptr = State.builder.structGEP(context, object.llvm_context_index, "")
            value = object.emitLinkValue(None)
            State.builder.store(value, obj_ptr)

        return context

    assert self.llvm_closure_type is not None

    return llvm.Value.null(llvm.Pointer.new(self.llvm_closure_type, 0))

#
# Contructor
#

@patch
def Constructor_emitEntry(self):
    self.llvm_context = State.builder.alloca(self.llvm_closure_type, "")

    self_var = State.builder.structGEP(self.llvm_context, 0, "")
    self_type = self.parent.parent.emitType()
    self_val = State.builder.alloca(self_type, "self")

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
def FunctionType_emitType(self):
    return llvm.Pointer.new(self.emitFunctionType(), 0)

@patch
def FunctionType_emitFunctionType(self, has_context = True):
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
# class FunctionInstance
#

@patch
def FunctionInstance_emitValue(self, type):
    return State.builder.load(self.emitAssignment(), "")

@patch
def FunctionInstance_emitAssignment(self):
    return State.self

@patch
def FunctionInstance_emitContext(self):
    return llvm.Value.null(llvm.Type.void_p())

#
# class ExternalFunction
#

@patch
def ExternalFunction_emit(self):
    if self.llvm_value is not None: return

    name = resolveName(self)
    func_type = self.type.emitFunctionType(False)
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
    type = type.resolveValue()

    if isinstance(type, lekvar.MethodType):
        return self.emitValueForMethodType(type)
    elif isinstance(type, lekvar.FunctionType):
        return self.resolveCall(type).emitValue(type)
    else:
        raise InternalError("Invalid value type for method")

@patch
def Method_emitValueForMethodType(self, type):
    values = []
    overloads = list(self.overload_context)
    for overload_type in type.used_overload_types:
        for index, overload in enumerate(overloads):
            if overload.resolveType().checkCompatibility(overload_type):
                values.append(overload.emitValue(overload_type))
                overloads.pop(index)
                break

    overloads = list(self.dependent_overload_context)
    for overload_type in type.used_dependent_overload_types:
        for overload in overloads:
            if overload.resolveType().checkCompatibility(overload_type):
                fn = overload.dependentTarget(overload_type)
                values.append(fn.emitValue(overload_type))
                break

    return llvm.Value.constStruct(type.emitType(), values)

@patch
def Method_emitContext(self):
    return None

#
# class MethodType
#

lekvar.MethodType.llvm_type = None

@patch
def MethodType_emitType(self):
    if self.llvm_type is None:
        fn_types = [type.emitType() for type in self.used_overload_types]
        fn_types += [type.emitType() for type in self.used_dependent_overload_types]
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
    return State.builder.load(self.emitAssignment(), "")

@patch
def MethodInstance_emitAssignment(self):
    value = State.self
    try:
        index = self.type.used_overload_types.index(self.target)
    except ValueError:
        index = len(self.type.used_overload_types)
        index += self.type.used_dependent_overload_types.index(self.target)

    return State.builder.structGEP(value, index, "")

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
def Class_emitValue(self, type):
    if type is None:
        type = self.resolveType()
    else:
        type = type.resolveValue()
        assert isinstance(type, lekvar.Class)

    attributes = [self.constructor.emitValue(type.instance_context[""].resolveType())]

    return llvm.Value.constStruct(type.emitType(), attributes)

@patch
def Class_emitType(self):
    if self.llvm_type is None:
        var_types = []

        for child in self.instance_context:
            if isinstance(child, lekvar.Variable):
                child.llvm_self_index = len(var_types)
                var_types.append(child.type.emitType())

        self.llvm_type = llvm.Struct.newAnonym(var_types, False)
    return self.llvm_type

@patch
def Class_emitContext(self):
    return None

#
# class Reference
#

@patch
def Reference_emitValue(self, type):
    value_type = self.value.resolveType()
    malloced = State.builder.malloc(referenceType(value_type.emitType()), "")
    value = State.builder.structGEP(malloced, 1, "")
    State.builder.store(emitValue(self.value, type), value)
    return malloced

@patch
def Reference_emitType(self):
    return llvm.Pointer.new(referenceType(self.value.emitType()), 0)

@patch
def Reference_emitInstanceValue(self, value, type):
    ref_value = self.value.emitInstanceValue(value, type)

    if type is not None and not isinstance(type, lekvar.Reference):
        value_ptr = State.builder.structGEP(ref_value, 1, "")
        return State.builder.load(value_ptr, "")
    return ref_value

@patch
def Reference_emitInstanceAssignment(self, value, type):
    ref_value = self.value.emitInstanceAssignment(value, type)

    if type is None or not isinstance(type, lekvar.Reference):
        loaded = State.builder.load(ref_value, "")
        return State.builder.structGEP(loaded, 1, "")
    return ref_value

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
