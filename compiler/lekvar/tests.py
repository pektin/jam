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

        with self.assertRaises(MissingReferenceError):
            test = tests.helloWorld()
            test.main.instructions = [
                Call("herroWorld", [])
            ]
            test.verify()

    def test_functionCalls(self):
        test = tests.functionCalls()
        test.verify()

    def test_assignments(self):
        test = tests.assignments()
        test.verify()

    def test_overloading(self):
        test = tests.overloading()
        test.verify()
