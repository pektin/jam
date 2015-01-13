import unittest
from .lekvar import *
from .errors import *

#
# Test Programs
#

class LekvarTests(unittest.TestCase):
    def helloWorld(self):
        return Module( {
            "helloWorld": Function([], [
                Call("print", [
                    Literal( LLVMType("String"), "Hello World!" )
                ] )
            ], None),
            "print" : ExternalFunction("puts", [LLVMType("String")], [LLVMType("Int")])
        }, Function([], [
            Call("helloWorld", [])
        ], []))

    def test_helloWorld(self):
        # def helloWorld()
        #     print("Hello World!")
        # helloWorld()

        # Standard Compilation test
        test = self.helloWorld()
        test.verify()

        with self.assertRaises(TypeError):
            test = self.helloWorld()
            test.main.instructions = [
                Call("helloWorld", [Literal( LLVMType("String"), "" )])
            ]
            test.verify()

        with self.assertRaises(TypeError):
            test = self.helloWorld()
            test.main.instructions = [
                Call("helloWorld", [Literal( LLVMType("String"), "" ), Literal( LLVMType("String"), "" )])
            ]
            test.verify()

        with self.assertRaises(ReferenceError):
            test = self.helloWorld()
            test.main.instructions = [
                Call("herroWorld", [])
            ]
            test.verify()
