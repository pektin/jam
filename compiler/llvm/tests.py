import unittest
from .bindings import *

from subprocess import check_output

BUILD_TARGET = "build/tests/llvm.ll"

class LLVMTests(unittest.TestCase):
    def test_llvm(self):
        i32 = Int.new(32)
        module = Module.fromName(b"test")
        builder = Builder.new()

        puts = module.addFunction(b"puts", Function.new(i32, [Pointer.new(Int.new(8), 0)], False))
        main = module.addFunction(b"main", Function.new(i32, [], False))

        entry = main.appendBlock(b"entry")
        return_ = main.appendBlock(b"return")

        builder.positionAtEnd(entry)
        hello = builder.globalString(b"Hello World!", b"temp.0")
        builder.call(puts, [hello], b"")
        builder.br(return_)

        builder.positionAtEnd(return_)
        builder.ret(Value.constInt(i32, 0, False))

        with open(BUILD_TARGET, "w") as f:
            f.write(module.toString().decode("UTF-8"))

        self.assertEqual(b"Hello World!\n", check_output(["lli " + BUILD_TARGET], shell=True))

