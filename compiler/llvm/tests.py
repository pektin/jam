import os
from subprocess import check_output

import pytest

from ..errors import ExecutionError

from .bindings import *
from .builtins import builtins
from .emitter import emit, run

BUILD_PATH = "build/tests"

def test_llvm():
    i32 = Int.new(32)
    module = Module.fromName("test")
    builder = Builder.new()

    puts = module.addFunction("puts", Function.new(i32, [Pointer.new(Int.new(8), 0)], False))
    main = module.addFunction("main", Function.new(i32, [], False))

    entry = main.appendBlock("entry")
    return_ = main.appendBlock("return")

    builder.positionAtEnd(entry)
    hello = builder.globalString("Hello World!", "temp.0")
    builder.call(puts, [hello], "")
    builder.br(return_)

    builder.positionAtEnd(return_)
    builder.ret(Value.constInt(i32, 0, False))

    os.makedirs(BUILD_PATH, exist_ok=True)
    with open(BUILD_PATH + "/llvm.ll", "wb") as f:
        f.write(module.toString())

    assert b"Hello World!\n" == check_output(["lli " + BUILD_PATH + "/llvm.ll"], shell=True)

def test_module_verification_handling():
    module = Module.fromName("test")
    builder = Builder.new()

    puts = module.addFunction("puts", Function.new(Type.void(), [Int.new(19)], False))
    main = module.addFunction("main", Function.new(Type.void(), [], False))

    entry = main.appendBlock("")
    builder.positionAtEnd(entry)

    hello = builder.globalString("Hello World!", "temp.0")
    builder.call(puts, [hello], "")

    with pytest.raises(Exception):
        module.verify()

def test_lli_failure():
    source = b"""
def rec() { ret rec() }
"""

    with pytest.raises(ExecutionError):
        run(source)

def test_builtin_lib():
    source = emit(builtins())

    os.makedirs(BUILD_PATH, exist_ok=True)
    with open(BUILD_PATH + "/builtins.ll", "wb") as f:
        f.write(source)

