import logging
from contextlib import contextmanager

from .. import lekvar

from . import bindings as llvm
from .util import *

# Global state for the llvm emitter
# Wraps a single llvm module
class State:
    @classmethod
    @contextmanager
    def begin(cls, logger:logging.Logger):
        cls.logger = logger

        # Dirty hack for circular import. Hook this state into the llvm bindigns
        llvm.State = cls

        cls.self = None
        cls.context = llvm.Context.new()
        #cls.context = llvm.Context.getGlobal()
        cls.builder = llvm.Builder.fromContext(cls.context)
        cls.module = llvm.Module.fromNameWithContext("", cls.context)
        cls.target_data = llvm.TargetData.new("")

        main_type = llvm.Function.new(cls.int(32), [], False)
        cls.main = cls.module.addFunction("main", main_type)
        cls.context.appendBlock(cls.main, "entry")
        main_exit = cls.context.appendBlock(cls.main, "exit")

        # Give a way for other things to have resettable data
        cls.data = {}

        yield

        cls.data = None

        # add a goto exit for the last block
        with cls.blockScope(cls.main.getLastBlock().getPrevious()):
            State.builder.br(main_exit)

        with cls.blockScope(main_exit):
            return_value = llvm.Value.constInt(cls.int(32), 0, False)
            cls.builder.ret(return_value)

    @classmethod
    def addMainInstructions(cls, instructions:[lekvar.Object]):
        last_block = cls.main.getLastBlock().getPrevious()
        with cls.blockScope(last_block):
            emitInstructions(instructions)

    @classmethod
    @contextmanager
    def blockScope(cls, block:llvm.Block):
        previous_block = cls.builder.position
        cls.builder.positionAtEnd(block)
        yield
        cls.builder.positionAtEnd(previous_block)

    @classmethod
    @contextmanager
    def selfScope(cls, self:llvm.Value):
        previous_self = cls.self
        cls.self = self
        yield
        cls.self = previous_self

    # Emmit an allocation as an instruction
    # Enforces allocation to happen early
    @classmethod
    def alloca(cls, type:llvm.Type, name:str = ""):
        # Find first block
        entry = cls.builder.position.function.getFirstBlock()

        with cls.blockScope(entry):
            cls.builder.positionAt(entry, entry.firstValue)
            value = cls.builder.alloca(type, name)
        return value

    # Get a value which is a pointer to a value
    # Requires an allocation
    @classmethod
    def pointer(cls, value):
        variable = State.alloca(value.type, "")
        State.builder.store(value, variable)
        return variable

    @classmethod
    def int(cls, bits):
        return llvm.Int.fromContext(cls.context, bits)

    @classmethod
    def half(cls):
        return llvm.Float.halfInContext(cls.context)

    @classmethod
    def float(cls):
        return llvm.Float.floatInContext(cls.context)

    @classmethod
    def double(cls):
        return llvm.Float.doubleInContext(cls.context)

    @classmethod
    def void_p(cls, space = 0):
        return llvm.Pointer.new(cls.int(8), space)

    @classmethod
    def struct(cls, values, packed = False):
        return llvm.Struct.newAnonymInContext(cls.context, values, packed)

    @classmethod
    def void(cls):
        return llvm.Type.voidFromContext(cls.context)

    # Create a reference type from a normal type
    @classmethod
    def referenceType(cls, type):
        return llvm.Struct.newAnonymInContext(cls.context, [cls.void_p(), type], False)
