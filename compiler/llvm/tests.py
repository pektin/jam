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
            ], LLVMType("Void")),
            "print" : ExternalFunction("puts", [LLVMType("String")], LLVMType("Int"))
        }, Function([], [
            Call("helloWorld", [])
        ], []))

    def test_helloWorld(self):
        test = self.helloWorld()
        test.verify()
        output = StringIO()
        emitter = Emitter(output)
        test.emitDefinition(emitter)
        emitter.finalize()
        print(output.getvalue())
