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
            "helloWorld": Method( { MethodSignature([]): [
                Call("print", [
                    Literal( LLVMType("String"), "Hello World!" )
                ] )
            ] } ),
            "print" : Method( { MethodSignature( [ LLVMType("String") ] ): [] } )
        }, [
            Call("helloWorld", [])
        ] )
        test.verify()

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
