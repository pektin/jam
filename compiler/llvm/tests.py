import os
from subprocess import check_output

from .bindings import *

BUILD_PATH = "build/tests"
BUILD_TARGET = "build/tests/llvm.ll"

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
    with open(BUILD_TARGET, "w") as f:
        f.write(module.toString().decode("UTF-8"))

    assert b"Hello World!\n" == check_output(["lli " + BUILD_TARGET], shell=True)

