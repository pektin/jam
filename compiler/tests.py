from .lekvar.lekvar import *

def helloWorld():
    # external puts as print
    # def helloWorld() {
    #     print("Hello World!")
    # }
    # helloWorld()
    #
    #=> Hello World!\n

    return Module( {
        "print" : ExternalFunction("puts", [LLVMType("String")], LLVMType("Int")), # external puts as print
        "helloWorld": Function([], [ # def helloWorld() {
            Call("print", [ # print(
                Literal( LLVMType("String"), "Hello World!" ) # "Hello World!"
            ] ) # )
        ], None), # }
    }, Function([], [
        Call("helloWorld", []) # helloWorld()
    ], None))
