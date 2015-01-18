import unittest
from io import StringIO
from tempfile import NamedTemporaryFile
import os, subprocess

from ..lekvar.lekvar import *
from .emitter import *
from .. import tests

class LLVMEmitterTest(unittest.TestCase):
    def compileRun(self, test, name):
        # Compile and run the generate llvm ir
        os.makedirs("builds", exist_ok=True)
        with open("builds/{}.ll".format(name), "w") as f:
            emitter = Emitter(f)
            test.emitDefinition(emitter)
            emitter.finalize()

        # Compile with clang, asserting no errors are found
        self.assertEqual(subprocess.call(
            ["clang -o builds/{} builds/{}.ll".format(name, name)
        ], shell=True), 0)
        # test output
        return subprocess.check_output(["builds/{}".format(name)]).decode("utf-8")

    def test_helloWorld(self):
        test = tests.helloWorld()
        test.verify()
        self.assertEqual(self.compileRun(test, "helloWorld"), "Hello World!\n")

    def test_functionCalls(self):
        test = tests.functionCalls()
        test.verify()
        self.assertEqual(self.compileRun(test, "functionCalls"), "1\n2\n")
