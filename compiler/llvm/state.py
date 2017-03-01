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
        cls.builder = llvm.Builder.new()
        cls.module = llvm.Module.fromName("")
        cls.target_data = llvm.TargetData.new("")

        main_type = llvm.Function.new(llvm.Int.new(32), [], False)
        cls.main = cls.module.addFunction("main", main_type)
        cls.main.appendBlock("entry")
        main_exit = cls.main.appendBlock("exit")

        yield

        # add a goto exit for the last block
        with cls.blockScope(cls.main.getLastBlock().getPrevious()):
            State.builder.br(main_exit)

        with cls.blockScope(main_exit):
            return_value = llvm.Value.constInt(llvm.Int.new(32), 0, False)
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
