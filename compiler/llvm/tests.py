import os
from subprocess import check_output

import pytest

from ..errors import *
from .. import llvm
from ..llvm import bindings as c

BUILD_PATH = "build/tests"

def test_llvm():
    i32 = c.Int.new(32)
    module = c.Module.fromName("test")
    builder = c.Builder.new()

    puts_type = c.Function.new(i32, [c.Pointer.new(c.Int.new(8), 0)], False)
    puts = module.addFunction("puts", puts_type)
    main = module.addFunction("main", c.Function.new(i32, [], False))

    entry = main.appendBlock("entry")
    return_ = main.appendBlock("return")

    builder.positionAtEnd(entry)
    hello = builder.globalString("Hello World!", "temp.0")
    builder.call(puts, [hello], "")
    builder.br(return_)

    builder.positionAtEnd(return_)
    builder.ret(c.Value.constInt(i32, 0, False))

    os.makedirs(BUILD_PATH, exist_ok=True)
    with open(BUILD_PATH + "/llvm.ll", "wb") as f:
        f.write(module.toString())

    assert b"Hello World!\n" == check_output(["lli " + BUILD_PATH + "/llvm.ll"], shell=True)

def test_module_verification_handling():
    module = c.Module.fromName("test")
    builder = c.Builder.new()

    puts = module.addFunction("puts", c.Function.new(c.Type.void(), [c.Int.new(19)], False))
    main = module.addFunction("main", c.Function.new(c.Type.void(), [], False))

    entry = main.appendBlock("")
    builder.positionAtEnd(entry)

    hello = builder.globalString("Hello World!", "temp.0")
    builder.call(puts, [hello], "")

    with pytest.raises(c.VerificationError):
        module.verify()

def test_lli_failure():
    source = b"""
def rec() { ret rec() }
"""

    with pytest.raises(ExecutionError):
        llvm.run(source)

def test_builtin_lib():
    source = llvm.emit(llvm.builtins())

    os.makedirs(BUILD_PATH, exist_ok=True)
    with open(BUILD_PATH + "/builtins.ll", "wb") as f:
        f.write(source)
