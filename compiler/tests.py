from .lekvar.lekvar import *

def helloWorld():
    # external puts as print
    # def helloWorld() {
    #     # Output: Hello World!
    #     print("Hello World!")
    # }
    # helloWorld()
    #
    #=> Hello World!\n

    return Module( {
        "print" : ExternalFunction("puts", [LLVMType("String")], LLVMType("Int")), # external puts as print
        "helloWorld": Function([], [ # def helloWorld() {
            Comment(" Output: Hello World!"),
            Call("print", [ # print(
                Literal( "Hello World!", LLVMType("String") ) # "Hello World!"
            ] ) # )
        ], None), # }
    }, Function([], [
        Call("helloWorld", []) # helloWorld()
    ], None))

def functionCalls():
    # external puts as print
    # def reprint(one:String, two:String) {
    #     print(one)
    #     return two
    #     print(two)
    # }
    # print(reprint("1", "2"))
    #
    #=> 1\n2\n

    return Module( {
        "print" : ExternalFunction("puts", [LLVMType("String")], LLVMType("Int")), # external puts as print
        "reprint": Function( [ Variable("one", LLVMType("String")), Variable("two", LLVMType("String")) ], [
            Call("print", [
                Reference("one")
            ] ),
            Return(Reference("two")),
            Call("print", [
                Reference("two")
            ] )
        ] )
    }, Function([], [
        Call("print", [
            Call("reprint", [
                Literal("1", LLVMType("String")),
                Literal("2", LLVMType("String"))
            ] )
        ] )
    ] ))

def assignments():
    # external puts as print
    # def assign() {
    #     foo = "1"
    #     bar = "2"
    #     foo = bar
    #     bar = "1"
    #     return foo
    # }
    # print(assign())
    #=> 2\n

    return Module( {
        "print" : ExternalFunction("puts", [LLVMType("String")], LLVMType("Int")),
        "assign": Function( [], [
            Assignment("foo", Literal("1", LLVMType("String"))),
            Assignment("bar", Literal("2", LLVMType("String"))),
            Assignment("foo", Reference("bar")),
            Assignment("bar", Literal("1", LLVMType("String"))),
            Return(Reference("foo")),
        ] )
    }, Function([], [
        Call("print", [
            Call("assign", []),
        ])
    ] ))

def overloading():
    # external puts as print
    # def puts() {
    #     print("Hello World")
    # }
    # def puts(string:String) {
    #     print(string)
    # }
    # def puts(string:String, string2:String) {
    #     print(string)
    #     print(string2)
    # }
    # puts()
    # puts("Testing")
    # puts("Hello", "World!")
    #=> Hello World\nTesting\nHello\nWorld!

    return Module( {
        "print" : ExternalFunction("puts", [LLVMType("String")], LLVMType("Int")),
        "puts" : Method( [
            Function([], [
                Call("print", [Literal("Hello World", LLVMType("String"))])
            ]),
            Function( [ Variable("string", LLVMType("String")) ], [
                Call("print", [Reference("string")])
            ] ),
            Function( [ Variable("string", LLVMType("String")), Variable("string2", LLVMType("String")) ], [
                Call("print", [Reference("string")]),
                Call("print", [Reference("string2")])
            ] )

        ] )
    }, Function([], [
        Call("puts", []),
        Call("puts", [ Literal("Testing", LLVMType("String")) ]),
        Call("puts", [ Literal("Hello", LLVMType("String")), Literal("World!", LLVMType("String")) ])
    ] ))
