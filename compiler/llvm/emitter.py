from contextlib import contextmanager
from io import IOBase

from ..lekvar.lekvar import *
from ..lekvar.errors import *

# Temporary until LLVMType is replaced
LLVMMAP = {
    "String": "i8*",
    "Int": "i32",
    "Void": "void",
}

class Emitter:
    output = None
    stack = None
    main = None

    def __init__(self, out:IOBase, library=False):
        self.output = out
        self.stack = []
        if not library:
            self.main = ""

    def finalize(self):
        # Finalize the emitter

        # Sanity Check
        if len(self.stack) != 0:
            raise InternalError("Emission stack item left at finalization")

        if self.main is not None:
            # Add main function
            self.writeGlobal("define i32 @main() {{\n{}ret i32 0\n}}".format(self.main))

    #
    # Output Writing
    #

    def writeGlobal(self, string):
        # Write directly to the global output
        self.output.write(string)

    def write(self, string, up=1):
        # Write to the stacked
        self.stack[-up] += string

    def writeMain(self, string):
        # Write directly to the main function
        main += string

    @property
    def in_line(self):
        return bool(self.stack[-1][-1] != "\n")

    @contextmanager
    def lineWrite(self, entry="", up=1):
        self.stack.append(entry)
        yield
        self.write(self.stack.pop(), up)

    @contextmanager
    def stackWrite(self, entry=""):
        self.stack.append(entry)
        yield
        self.writeGlobal(self.stack.pop())

    #
    # Name Generation
    #

    def resolveName(self, scope:Scope):
        # Resolves the name of a scope, starting with a extraneous .
        name = ""
        while scope.name is not None:
            name += "." + scope.name
            scope = scope.parent
        return name

    temp_name_index = 0
    def getTempName(self):
        # Return a temporary, but unique name. Temporary names always start with temp
        name = "temp.{}".format(self.temp_name_index)
        self.temp_name_index += 1
        return name

    #
    # LLVM IR Emission
    #

    def addMain(self, main:Function):
        # adds a function to the "main" function. Added function must be void(void) and emitted
        # Ignore for libraries
        if self.main is None:
            return

        self.main += "call void @{}()\n".format(main.emit_data)

    def emitExternalFunction(self, function:ExternalFunction):
        # declare <return> @<name>(<arguments>)\n
        with self.stackWrite("declare "):

            function.return_type.emit(self) # return
            self.write(" @{}(".format(function.external_name)) # name

            for index, argument in enumerate(function.arguments): # arguments
                if index > 0:
                    self.write(",")
                argument.emit(self)
            self.write(")\n")

        return function.external_name

    @contextmanager
    def emitFunction(self, function:Function):
        # Temporarily functions only return void and have no arguments

        # define <return> @<name>(<arguments>) {
        # yield <name>
        # label.return:
        # ret <return>
        # }
        name = "lekvar" + self.resolveName(function) # name
        with self.stackWrite("define "):
            not_void = function.return_type is not None

            if not_void:
                function.return_type.emit(self) # return
            else:
                self.write("void")

            self.write(" @{}(".format(name))
            for index, argument in enumerate(function.arguments): # arguments
                if index > 0:
                    self.write(",")
                argument.emit(self)
            self.write(") {\n")

            if not_void:
                self.write("%return = alloca ")
                function.return_type.emit(self)
                self.write("\n")

            yield name

            self.write("br label %label.return\nlabel.return:\n")
            if not_void:
                self.write("%return.value = load ")
                function.return_type.emit(self)
                self.write("* %return\nret ")
                function.return_type.emit(self)
                self.write(" %return.value\n")
            else:
                self.write("ret void\n")
            self.write("}\n")

    def emitFunctionValue(self, function:Function):
        # <return> @<name>
        if function.return_type is not None:
            function.return_type.emit(self) # return
        else:
            self.write("void")
        self.write(" @{}".format(function.emit_data)) # name

    def emitLiteral(self, literal:Literal):
        # Emit a non-specific literal
        type = literal.resolveType()

        if not isinstance(type, LLVMType): #TODO: Get rid of LLVMType
            raise NotImplemented()

        if type.llvm_type == "String":
            if literal.emit_data is None:
                # Create a global constant for it
                literal.emit_data = self.getTempName()
                # @<tempname> = internal constant [<size> x i8] c"<string>\00"
                self.writeGlobal("@{} = internal constant [{} x i8] c\"{}\\00\"\n".format(literal.emit_data, len(literal.data) + 1, literal.data))
            # i8* getelementptr inbounds ([<size> x i8]* @<tempname>, i32 0, i32 0)
            self.write("i8* getelementptr inbounds ([{} x i8]* @{}, i32 0, i32 0)".format(len(literal.data) + 1, literal.emit_data))
        else:
            raise NotImplemented()

    def emitCall(self, call:Call):
        # Since you can't nest calls in llvm, use a temporary variable to store the returned value

        def emit():
            # <function>(<arguments>)\n
            call.called.emit(self) # function
            self.write("(")
            for index, value in enumerate(call.values): # arguments
                if index > 0:
                    self.write(",")
                value.emit(self)
            self.write(")\n")

        if self.in_line:
            print(self.stack)
            #.. %<temp> = call <emit>
            call.emit_data = self.getTempName() # temp
            with self.lineWrite("%{} = call ".format(call.emit_data), 2):
                emit()
            call.called.return_type.emit(self)
            self.write(" %{}".format(call.emit_data))

        else:
            # call <emit>
            with self.lineWrite("call "):
                emit()

    def emitReturn(self, ret:Return):
        if ret.parent.return_type is not None:
            self.write("store ")
            ret.value.emit(self)
            self.write(", ")
            ret.parent.return_type.emit(self)
            self.write("* %return\n")
        self.write("br label %label.return\n")

    def emitLLVMType(self, type:LLVMType):
        # just map the mentioned type to a llvm type
        self.write(LLVMMAP[type.llvm_type])

    def emitVariable(self, var:Variable):
        var.type.emit(self)
        self.write(" %lekvar.{}".format(var.name))
