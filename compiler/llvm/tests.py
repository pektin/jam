import unittest
from io import StringIO
from tempfile import NamedTemporaryFile
import os, subprocess

from ..lekvar.lekvar import *
from .emitter import *
from .. import tests

class LLVMEmitterTest(unittest.TestCase):
    def test_helloWorld(self):
        test = tests.helloWorld()
        test.verify()

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
        self.assertEqual(output, "Hello World!\n")
