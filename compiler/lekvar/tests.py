import unittest
from .lekvar import *
from .errors import *

#
# Test Programs
#

class LekvarTests(unittest.TestCase):
    def test_helloWorld(self):
        # def helloWorld()
        #     print("Hello World!")
        # helloWorld()

        # Standard Compilation test
        test = Module( {
            "helloWorld": Function([], [
                Call("print", [
                    Literal( LLVMType("String"), "Hello World!" )
                ] )
            ], None),
            "print" : ExternalFunction("puts", [LLVMType("String")], [LLVMType("Int")])
        }, [
            Call("helloWorld", [])
        ] )
        test.verify()

        #DEBUG
        #from ..llvm.emitter import Emitter
        #import sys
        #test.emit(Emitter(sys.stdout))

        with self.assertRaises(TypeError):
            test.main = [
                Call("helloWorld", [Literal( LLVMType("String"), "" )])
            ]
            test.verify()

        with self.assertRaises(TypeError):
            test.main = [
                Call("helloWorld", [Literal( LLVMType("String"), "" ), Literal( LLVMType("String"), "" )])
            ]
            test.verify()

        with self.assertRaises(ReferenceError):
            test.main = [
                Call("herroWorld", [])
            ]
            test.verify()


if __name__ == "__main__":
    unittest.main(verbosity=2)
