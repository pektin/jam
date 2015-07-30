import os
from subprocess import check_output

import pytest

from ..errors import ExecutionError

from . import bindings as llvm
from .builtins import builtins
from .emitter import emit, run

BUILD_PATH = "build/tests"

def test_llvm():
    i32 = llvm.Int.new(32)
    module = llvm.Module.fromName("test")
    builder = llvm.Builder.new()

    puts_type = llvm.Function.new(i32, [llvm.Pointer.new(llvm.Int.new(8), 0)], False)
    puts = module.addFunction("puts", puts_type)
    main = module.addFunction("main", llvm.Function.new(i32, [], False))

    entry = main.appendBlock("entry")
    return_ = main.appendBlock("return")

    builder.positionAtEnd(entry)
    hello = builder.globalString("Hello World!", "temp.0")
    builder.call(puts, [hello], "")
    builder.br(return_)

    builder.positionAtEnd(return_)
    builder.ret(llvm.Value.constInt(i32, 0, False))

    os.makedirs(BUILD_PATH, exist_ok=True)
    with open(BUILD_PATH + "/llvm.ll", "wb") as f:
        f.write(module.toString())

    assert b"Hello World!\n" == check_output(["lli " + BUILD_PATH + "/llvm.ll"], shell=True)

def test_module_verification_handling():
    module = llvm.Module.fromName("test")
    builder = llvm.Builder.new()

    puts = module.addFunction("puts", llvm.Function.new(llvm.Type.void(), [llvm.Int.new(19)], False))
    main = module.addFunction("main", llvm.Function.new(llvm.Type.void(), [], False))

    entry = main.appendBlock("")
    builder.positionAtEnd(entry)

    hello = builder.globalString("Hello World!", "temp.0")
    builder.call(puts, [hello], "")

    with pytest.raises(llvm.VerificationError):
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

