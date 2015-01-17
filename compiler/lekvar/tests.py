import unittest

from .lekvar import *
from .errors import *
from .. import tests

class LekvarTests(unittest.TestCase):
    def test_helloWorld(self):
        # Standard Compilation test
        test = tests.helloWorld()
        test.verify()

        with self.assertRaises(TypeError):
            test = tests.helloWorld()
            test.main.instructions = [
                Call("helloWorld", [Literal( LLVMType("String"), "" )])
            ]
            test.verify()

        with self.assertRaises(TypeError):
            test = tests.helloWorld()
            test.main.instructions = [
                Call("helloWorld", [Literal( LLVMType("String"), "" ), Literal( LLVMType("String"), "" )])
            ]
            test.verify()

        with self.assertRaises(ReferenceError):
            test = tests.helloWorld()
            test.main.instructions = [
                Call("herroWorld", [])
            ]
            test.verify()
