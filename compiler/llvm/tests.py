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

        # Run the bytecode with lli
        return subprocess.check_output("lli builds/{}.ll".format(name), shell=True)

    def test_helloWorld(self):
        test = tests.helloWorld()
        test.verify()
        self.assertEqual(self.compileRun(test, "helloWorld"), b"Hello World!\n")

    def test_functionCalls(self):
        test = tests.functionCalls()
        test.verify()
        self.assertEqual(self.compileRun(test, "functionCalls"), b"1\n2\n")
