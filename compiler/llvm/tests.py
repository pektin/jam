import unittest
from io import StringIO

from ..lekvar.lekvar import *
from .emitter import *

class LLVMEmitterTest(unittest.TestCase):
    def helloWorld(self): #TODO: Standardise tests
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
        test = self.helloWorld()
        test.verify()
        output = StringIO()
        test.emit(Emitter(output))
        print(output.getvalue())
