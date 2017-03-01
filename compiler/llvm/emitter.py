from abc import abstractmethod as abstract
from itertools import chain
from contextlib import contextmanager, ExitStack

from .. import lekvar
from ..errors import InternalError, TypeError

from .state import State
from .util import *
from . import bindings as llvm

# Abstract extensions

lekvar.BoundObject.llvm_value = None

# Extension abstract methods apparently don't work

@patch
def Object_resetLocalEmission(self):
    raise InternalError("Not Implemented")

@patch
def Object_gatherEmissionResets(self):
    return []

@patch
#@abstract
def Object_emitValue(self, type:lekvar.Type) -> llvm.Value:
    raise InternalError("Not Implemented")

@patch
#@abstract
def Object_emitCallable(self, type:lekvar.Type) -> llvm.Value:
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
def Type_emitInstanceCallable(self, value:lekvar.Object, type:lekvar.Type) -> llvm.Value:
    return value.emitCallable(type)

@patch
def Type_emitInstanceAssignment(self, value:lekvar.Object, type:lekvar.Type) -> llvm.Value:
    return value.emitAssignment(type)

#
# class Object
#

# Context for resetting the emission of a value
@patch
def Object_resetEmission(self):
    cache = set()
    stack = ExitStack()
    objects = iter([self])

    while True:
        obj = next(objects, None)
        if obj is None: break
        if obj in cache: continue

        cache.add(obj)
        local_resets = obj.resetLocalEmission()
        if local_resets is not None:
            stack.enter_context(local_resets)
        objects = chain(objects, obj.gatherEmissionResets())

    return stack

#
# class Link
#

@patch
def Link_resetLocalEmission(self):
    return self.value.resetLocalEmission()

@patch
def Link_gatherEmissionResets(self):
    return self.value.gatherEmissionResets()

@patch
def Link_emit(self):
    return self.value.emit()

@patch
def Link_emitValue(self, type):
    if self.value is None: return
    return self.value.emitValue(type)

@patch
def Link_emitCallable(self, type):
    return self.value.emitCallable(type)

@patch
def Link_emitAssignment(self, type):
    return self.value.emitAssignment(type)

@patch
def Link_emitType(self):
    return self.value.emitType()

@patch
def Link_emitContext(self):
    return self.value.emitContext()

@patch
def Link_emitInstanceValue(self, value, type):
    return self.value.emitInstanceValue(value, type)

@patch
def Link_emitInstanceCallable(self, value, type):
    return self.value.emitInstanceCallable(value, type)

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
    with State.selfScope(emitAssignment(self.object, None)):
        return self.value.emitContext()

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

    data = emitConstant(self.data)

    return llvm.Value.constStruct(struct_type, [data])

@patch
def Literal_emitAssignment(self, type):
    return State.pointer(self.emitValue(None))

def emitConstant(value):
    if isinstance(value, str):
        return State.builder.globalString(value, "")
    elif isinstance(value, bool):
        return llvm.Value.constInt(llvm.Int.new(1), value, False)
    elif isinstance(value, int):
        return llvm.Value.constInt(llvm.Int.new(64), value, False)
    elif isinstance(value, float):
        return llvm.Value.constFloat(llvm.Float.double(), value)
    elif isinstance(value, dict) and len(value) == 1 and "value" in value:
        return emitConstant(value["value"].data)
    else:
        raise InternalError("Not Implemented")

#
# class Variable
#

lekvar.Variable.llvm_context_index = -1
lekvar.Variable.llvm_self_index = -1

@patch
@contextmanager
def Variable_resetLocalEmission(self):
    old_value = self.llvm_value
    self.llvm_value = None
    yield
    self.llvm_value = old_value

@patch
def Variable_emit(self):
    if self.value is not None: return
    if (self.llvm_value is not None or
        self.llvm_context_index >= 0 or
        self.llvm_self_index >= 0): return

    type = self.type.emitType()
    name = resolveName(self)
    if self.stats.static:
        self.llvm_value = State.module.addVariable(type, name)
        self.llvm_value.initializer = llvm.Value.undef(type)
    else:
        self.llvm_value = State.alloca(type, name)

@patch
def Variable_emitValue(self, type):
    if self.value is not None:
        return self.value.emitValue(type)

    self.emit()

    return State.builder.load(self.emitAssignment(type), "")

@patch
def Variable_emitAssignment(self, type):
    if self.value is not None:
        return self.value.emitAssignment(type)

    self.emit()

    if self.llvm_value is not None:
        return self.llvm_value

    if self.llvm_self_index < 0:
        raise InternalError()

    assert State.self is not None and State.self is not 0
    return State.builder.structGEP(State.self, self.llvm_self_index, "")

@patch
def Variable_emitType(self):
    if self.value is None:
        # This check should be done during verification
        raise TypeError(message="Not Implemented")

    return self.value.emitType()

@patch
def Variable_emitContext(self):
    if self.value is not None:
        return self.value.emitContext()
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

    for child in self.context:
        child.emit()

    State.addMainInstructions(self.main)

@patch
def Module_emitValue(self):
    raise InternalError("Not Implemented") #TODO: Implement Method values

#
# class Call
#

@patch
def Call_emitValue(self, type):
    # Ugly hack for handling the sizeof function
    # Avoids a function call completely
    if isinstance(self.function.extractValue(), lekvar.SizeOf):
        return self.emitSizeOf(self.values[0])

    with State.selfScope(self.called.emitAssignment(type)):
        called = self.called.resolveType().resolveValue().emitInstanceCallable(self.function, self.function_type)

    bound_value = self.called.emitContext()
    with State.selfScope(bound_value):
        context = self.function.emitContext()

    if context is not None:
        arguments = [State.builder.cast(context, llvm.Type.void_p(), "")]
    else:
        arguments = []

    # Hack, for now
    scope = ExitStack()
    if isinstance(self.function, lekvar.ForwardTarget):
        scope = self.function.target()

    # TODO: Emit arguments before function
    with scope:
        argument_types = self.function.resolveType().extractValue().arguments
        arguments += [emitValue(value, type) for value, type in zip(self.values, argument_types)]

    # Get the llvm function type
    return State.builder.call(called, arguments, "")

@patch
def Call_emitSizeOf(self, type):
    type = type.resolveValue().emitType()

    size = State.target_data.storeSizeOf(type)
    literal = lekvar.Literal(size, self.resolveType())
    return literal.emitValue(None)

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
def Context_gatherEmissionResets(self):
    for child in self:
        yield child

@patch
@contextmanager
def Context_resetLocalEmission(self):
    old_type = self.llvm_type
    self.llvm_type = None
    yield
    self.llvm_type = old_type

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
        if child.stats.static: continue

        child.llvm_context_index = index
        index += 1
        types.append(child.resolveType().emitType())

    if len(types) == 0:
        types = [llvm.Pointer.void_p()]

    self.llvm_type = llvm.Struct.newAnonym(types, False)

    return self.llvm_type

#
# class ForwardObject
#

@patch
def ForwardObject_gatherEmissionResets(self):
    if self.target is None:
        return []
    assert self.target is not None
    return self.target.gatherEmissionResets()

@patch
def ForwardObject_resetLocalEmission(self):
    if self.target is None:
        return
    assert self.target is not None
    return self.target.resetLocalEmission()

@patch
def ForwardObject_emit(self):
    assert self.target is not None
    self.target.emit()

@patch
def ForwardObject_emitValue(self, type):
    assert self.target is not None
    return self.target.emitValue(type)

@patch
def ForwardObject_emitCallable(self, type):
    assert self.target is not None
    return self.target.emitCallable(type)

@patch
def ForwardObject_emitType(self):
    assert self.target is not None
    return self.target.emitType()

@patch
def ForwardObject_emitContext(self):
    assert self.target is not None
    return self.target.emitContext()

#
# class ForwardTarget
#

lekvar.ForwardTarget.emitted = False

@patch
def ForwardTarget_emit(self):
    raise InternalError("Not Implemented")

@patch
def ForwardTarget_emitValue(self, type):
    if len(self.dependencies) == 0:
        return self.value.emitValue(type)

    if self.value.emitted_cache is None:
        self.value.emitted_cache = {}
    cache = self.value.emitted_cache

    with self.target():
        #TODO: Make this generic, currently specific for Function
        # Maybe turn the entire emitter into a sequenced collection of generators,
        # like forward object targeting, which would also allow for multithreading
        assert isinstance(self.value, lekvar.Function)

        if type not in cache:
            assert not self.emitted

            with self.value.resetEmission():
                self.value.emitStatic()
                cache[type] = self.value.llvm_value
                self.value.emitBody()
        return cache[type]

@patch
def ForwardTarget_emitCallable(self, type):
    if len(self.dependencies) == 0:
        return self.value.emitCallable(type)

    if self.value.emitted_cache is None:
        self.value.emitted_cache = {}
    cache = self.value.emitted_cache

    with self.target():
        assert isinstance(self.value, lekvar.Function)

        if type not in cache:
            assert not self.emitted

            with self.value.resetEmission():
                self.value.emitStatic()
                cache[type] = self.value.llvm_value
                self.value.emitBody()
        return cache[type]

@patch
def ForwardTarget_emitContext(self):
    with self.target():
        return self.value.emitContext()

#
# class ClosedLink
#

lekvar.ClosedLink.llvm_value = None

@patch
def ClosedLink_gatherEmissionResets(self):
    return []

@patch
@contextmanager
def ClosedLink_resetLocalEmission(self):
    old_value = self.llvm_value
    self.llvm_value = None
    yield
    self.llvm_value = old_value

@patch
def ClosedLink_emitValue(self, type):
    if self.llvm_value is None:
        return self.value.emitValue(type)
    return State.builder.load(self.emitAssignment(type), "")

@patch
def ClosedLink_emitAssignment(self, type):
    if self.llvm_value is None:
        return self.value.emitAssignment(type)
    return self.llvm_value

@patch
def ClosedLink_emitLinkValue(self, type):
    return self.value.emitValue(type)

#
# class ClosedTarget
#

lekvar.ClosedTarget.llvm_value = None
lekvar.ClosedTarget.llvm_type = None

@patch
def ClosedTarget_emitValue(self, type):
    # if self.llvm_value is None:
    with self.target():
        with self.origin.resetEmission():
            # self.llvm_value = self.value.emitValue(type)
            return self.value.emitValue(type)

    # return self.llvm_value

@patch
def ClosedTarget_emitCallable(self, type):
    with self.target():
        with self.origin.resetEmission():
            return self.value.emitCallable(type)

@patch
def ClosedTarget_emitContext(self):
    with self.target():
        with self.origin.resetEmission():
            return self.value.emitContext()

@patch
def ClosedTarget_emitType(self):
    # if self.llvm_type is None:
    with self.target():
        with self.origin.resetEmission():
            # self.llvm_type = self.value.emitType()
            return self.value.emitType()

    # return self.llvm_type
#
# class Function
#

lekvar.Function.llvm_return = None
lekvar.Function.llvm_context = None
lekvar.Function.llvm_closure_type = None
lekvar.Function.emitted_cache = None

@patch
def Function_gatherEmissionResets(self):
    yield self.closed_context

    if "self" in self.closed_context:
        yield self.closed_context["self"].resolveType()

    for child in self.local_context:
        yield child

@patch
@contextmanager
def Function_resetLocalEmission(self):
    old_value = self.llvm_value
    self.llvm_value = None
    old_closure_type = self.llvm_closure_type
    self.llvm_closure_type = None
    yield
    self.llvm_value = old_value
    self.llvm_closure_type = old_closure_type

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

    if not self.stats.static:
        self.llvm_value.visibility = llvm.Visibility.hidden

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
        assert self.closed_context["self"].llvm_context_index >= 0
        index = self.closed_context["self"].llvm_context_index
        self_value = State.builder.structGEP(self.llvm_context, index, "")
        self_value = State.builder.load(self_value, "")
        self_stack.enter_context(State.selfScope(self_value))

    with self_stack:
        for object in self.closed_context:
            if object.name == "self": continue
            if object.stats.static: continue

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

    struct_type = self.type.emitType()
    context = self.emitContext(malloc = True)
    context = State.builder.cast(context, llvm.Pointer.void_p(), "")

    delegate = llvm.Value.constStruct(struct_type, [self.llvm_value, llvm.Value.undef(llvm.Type.void_p())])

    return State.builder.insertValue(delegate, context, 1, "")

@patch
def Function_emitCallable(self, type):
    self.emit()

    return self.llvm_value

@patch
def Function_emitContext(self, malloc = False, store_self = True):
    closure_type = self.llvm_closure_type or self.closed_context.emitType()
    assert closure_type is not None

    if len(self.closed_context) > 0:
        if malloc:
            context = State.builder.malloc(closure_type, "context")
        else:
            context = State.alloca(closure_type, "")

        #TODO: Remove this special case
        if "self" in self.closed_context and store_self:
            assert State.self is not None
            assert self.closed_context["self"].llvm_context_index >= 0
            index = self.closed_context["self"].llvm_context_index
            self_ptr = State.builder.structGEP(context, index, "")
            State.builder.store(State.self, self_ptr)

        for object in self.closed_context:
            if object.name == "self": continue
            if object.stats.static: continue

            obj_ptr = State.builder.structGEP(context, object.llvm_context_index, "")
            value = object.emitLinkValue(None)
            State.builder.store(value, obj_ptr)

        return context

    return llvm.Value.null(llvm.Pointer.new(closure_type, 0))

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
def Constructor_emitContext(self, malloc = False):
    # TODO: Add inits here
    return lekvar.Function.emitContext(self, malloc = malloc, store_self = False)

#
# class FunctionType
#

@patch
def FunctionType_gatherEmissionResets(self):
    if self.return_type is not None:
        yield self.return_type

    for type in self.arguments:
        yield type

@patch
def FunctionType_resetLocalEmission(self):
    return None

@patch
def FunctionType_emitType(self):
    func = llvm.Pointer.new(self.emitFunctionType(), 0)
    context = llvm.Type.void_p()

    return llvm.Struct.newAnonym([func, context], False)

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
def FunctionInstance_emitCallable(self, type):
    delegate = self.emitAssignment()
    func = State.builder.structGEP(delegate, 0, "")
    return State.builder.load(func, "")

@patch
def FunctionInstance_emitAssignment(self):
    return State.self

@patch
def FunctionInstance_emitContext(self):
    delegate = self.emitAssignment()
    context = State.builder.structGEP(delegate, 1, "")
    return State.builder.load(context, "")

#
# class ExternalFunction
#

@patch
def ExternalFunction_emit(self):
    if self.llvm_value is not None: return

    name = resolveName(self)
    func_type = self.type.emitFunctionType(False)
    self.llvm_value = State.module.addFunction(self.external_name, func_type)

@patch
def ExternalFunction_emitValue(self, type):
    self.emit()
    return self.llvm_value

@patch
def ExternalFunction_emitCallable(self, type):
    self.emit()
    return self.llvm_value

@patch
def ExternalFunction_emitContext(self):
    return None

#
# class Method
#

@patch
def Method_gatherEmissionResets(self):
    yield self.overload_context

@patch
def Method_resetLocalEmission(self):
    return None

@patch
def Method_emit(self):
    for overload in self.overload_context:
        if not overload.stats.forward:
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

    for index, overload_type in enumerate(type.used_overload_types):
        normal_matches = []
        forward_matches = []

        for overload in self.overload_context:
            if overload.resolveType().checkCompatibility(overload_type):
                if overload.stats.forward:
                    forward_matches.append(overload)
                else:
                    normal_matches.append(overload)

        if len(normal_matches) > 0:
            assert len(normal_matches) == 1
            overload = normal_matches[0]
            value = emitValue(overload, overload_type)
        else:
            assert len(forward_matches) == 1
            overload = forward_matches[0]
            fn = overload.forwardTarget(overload_type)
            value = emitValue(fn, overload_type)

        values.append(value)

    return newStruct(State.builder, type.emitType(), values)

@patch
def Method_emitContext(self):
    return State.self

#
# class MethodType
#

lekvar.MethodType.llvm_type = None

@patch
def MethodType_gatherEmissionResets(self):
    for fn_type in self.used_overload_types:
        yield fn_type

@patch
def MethodType_resetLocalEmission(self):
    return None

@patch
def MethodType_emitType(self):
    if self.llvm_type is None:
        fn_types = [type.emitType() for type in self.used_overload_types]
        self.llvm_type = llvm.Struct.newAnonym(fn_types, False)
    return self.llvm_type

#
# class MethodInstance
#

@patch
def MethodInstance_emit(self):
    pass

@patch
@contextmanager
def MethodInstance_targetEmitScope(self):
    value = State.self
    assert value is not None
    index = self.type.used_overload_types.index(self.target.type)
    delegate = State.builder.structGEP(value, index, "")

    with State.selfScope(delegate):
        yield

@patch
def MethodInstance_emitValue(self, type):
    with self.targetEmitScope():
        return self.target.emitValue(type)

@patch
def MethodInstance_emitCallable(self, type):
    with self.targetEmitScope():
        return self.target.emitCallable(type)

@patch
def MethodInstance_emitAssignment(self):
    with self.targetEmitScope():
        return self.target.emitAssignment()

@patch
def MethodInstance_emitContext(self):
    with self.targetEmitScope():
        return self.target.emitContext()

#
# class Class
#

lekvar.Class.llvm_type = None

@patch
def Class_gatherEmissionResets(self):
    yield self.constructor

    for child in self.instance_context:
        yield child

@patch
@contextmanager
def Class_resetLocalEmission(self):
    old_type = self.llvm_type
    self.llvm_type = None
    yield
    self.llvm_type

@patch
def Class_emit(self):
    if self.constructor is not None:
        self.constructor.emit()

    for child in self.instance_context:
        child.emit()

@patch
def Class_emitValue(self, type):

    if type is None:
        type = class_type = self.resolveType()
    else:
        if isinstance(type.extractValue(), lekvar.VoidType):
            return llvm.Value.null(type.emitType())

        class_type = type.extractValue()
        assert isinstance(class_type, lekvar.Class)
        type = type.resolveValue()

    attributes = []

    # TODO: Expand to include other 'static' properties of classes
    if self.constructor is not None and "" in class_type.instance_context:
        value = self.constructor.emitValue(class_type.instance_context[""].resolveType())
        attributes.append(value)

    return newStruct(State.builder, type.emitType(), attributes)

@patch
def Class_emitAssignment(self, type):
    return State.pointer(self.emitValue(type))

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
# class MetaClass
#

@patch
def MetaClass_emitInstanceCallable(self, instance, type):
    # No need to do anything if we're calling a constructor directly
    if isinstance(instance.extractValue(), lekvar.Constructor):
        return instance.emitCallable(type)

    value = State.self
    constructor = State.builder.structGEP(value, 0, "")

    with State.selfScope(constructor):
        return instance.emitCallable(type)

#
# class Reference
#

@patch
def Reference_emitValue(self, type):
    assert isinstance(type, lekvar.Reference)
    type = type.value

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

#
# class SizeOf
#

@patch
def SizeOf_emit(self):
    # Don't bother
    return

#
# class VoidType
#

@patch
def VoidType_emit(self):
    return

@patch
def VoidType_emitType(self):
    return llvm.Type.void_p()

@patch
def VoidType_emitInstanceValue(self, value, type):
    value = value.emitValue(type)
    if isinstance(type.resolveValue(), lekvar.VoidType):
        return value
    value = State.builder.cast(value, llvm.Pointer.new(type.emitType(), 0), "")
    return State.builder.load(value, "")

@patch
def VoidType_emitInstanceAssignment(self, value, type):
    value = value.emitAssignment(type)
    if isinstance(type.resolveValue(), lekvar.VoidType):
        return value
    value = State.builder.load(value, "")
    return State.builder.cast(value, llvm.Pointer.new(type.emitType(), 0), "")
