import unittest
from io import StringIO
from tempfile import NamedTemporaryFile
import os, subprocess

from ..lekvar.lekvar import *
from .emitter import *

class LLVMEmitterTest(unittest.TestCase):
    def helloWorld(self): #TODO: Standardise tests
        test = Module( {
            "helloWorld": Function([], [
                Call("print", [
                    Literal( LLVMType("String"), "Hello World!" )
                ] )
            ], LLVMType("Void")),
            "print" : ExternalFunction("puts", [LLVMType("String")], LLVMType("Int"))
        }, Function([], [
            Call("helloWorld", [])
        ], []))
        test.verify()
        return test

    def test_helloWorld(self):
        test = self.helloWorld()

        # Compile and run the generate llvm ir
        os.makedirs("builds", exist_ok=True)
        with open("builds/helloWorld.ll", "w") as f:
            emitter = Emitter(f)
            test.emitDefinition(emitter)
            emitter.finalize()

        # Compile with clang, asserting no errors are found
        self.assertEqual(subprocess.call(["clang -o builds/helloWorld builds/helloWorld.ll"], shell=True), 0)
        # test output
        output = subprocess.check_output(["builds/helloWorld"]).decode("utf-8")
        print(output)
        self.assertEqual(output, "Hello World!\n")
