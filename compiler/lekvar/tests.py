import unittest
from lekvar import *

#
# Test Programs
#

class Test(unittest.TestCase):
    def test_helloWorld(self):
        # def helloWorld()
        #     print("Hello World!")
        # helloWorld()

        test = Module( {
            "helloWorld": Method( MethodSignature([], []), [
                Call("print", [
                    Literal("String", "Hello World!")
                ] )
            ] )
        }, Method(None, [
            Call("helloWorld", [])
        ] ) )
        test.verify()

unittest.main()
