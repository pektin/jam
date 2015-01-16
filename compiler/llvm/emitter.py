from contextlib import contextmanager
from io import IOBase

from ..lekvar.lekvar import *
from ..lekvar.errors import *

# Temporary
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

    def addMain(self, main:Function):
        if self.main is None:
            return

        # main is assumed to be void(void) and already emitted
        self.main += "  call void @{}()\n".format(main.emit_data)

    def finalize(self):
        if len(self.stack) != 0:
            raise None #TODO: Proper Error Message

        if self.main is not None:
            # Add main function
            self.output.write("define i32 @main() {{\n{}  ret i32 0\n}}".format(self.main))

    def resolveName(self, scope:Scope):
        name = ""
        while scope.name is not None:
            name += "." + scope.name
            scope = scope.parent
        return name

    temp_name_index = 0
    def getTempName(self):
        # Return a temporary, but unique name
        name = "temp.{}".format(self.temp_name_index)
        self.temp_name_index += 1
        return name

    def emitExternalFunction(self, function:ExternalFunction):
        self.stack.append("declare ")
        function.return_type.emit(self)
        self.stack[-1] += " @{}(".format(function.external_name)
        for index, argument in enumerate(function.arguments):
            if index > 0:
                self.stack[-1] += ","
            argument.emit(self)
        self.stack[-1] += ")\n"
        self.output.write(self.stack.pop())
        return function.external_name

    @contextmanager
    def emitFunction(self, function:Function):
        self.stack.append("")
        name = "lekvar" + self.resolveName(function)
        yield name
        out = "define void @{}() {{\n{}  ret void\n}}\n".format(name, self.stack.pop())
        self.output.write(out)

    def emitFunctionValue(self, function:Function):
        function.return_type.emit(self)
        print(function.emit_data)
        self.stack[-1] += " @{}".format(function.emit_data)

    def emitLiteral(self, literal:Literal):
        type = literal.resolveType()

        if not isinstance(type, LLVMType):
            raise NotImplemented()

        if type.llvm_type == "String":
            if literal.emit_data is None:
                # Create a global constant for it
                literal.emit_data = self.getTempName()
                self.output.write("@{} = internal constant [{} x i8] c\"{}\\00\"\n".format(literal.emit_data, len(literal.data) + 1, literal.data))
            self.stack[-1] += "i8* getelementptr inbounds ([{} x i8]* @{}, i32 0, i32 0)".format(len(literal.data) + 1, literal.emit_data)
        else:
            raise NotImplemented()

    def emitCall(self, call:Call):
        self.stack[-1] += "  call "
        call.called.emit(self)
        print(self.stack)
        self.stack[-1] += "("
        for index, value in enumerate(call.values):
            if index > 0:
                self.stack[-1] += ","
            value.emit(self)
        self.stack[-1] += ")\n"

    def emitLLVMType(self, type:LLVMType):
        self.stack[-1] += LLVMMAP[type.llvm_type]
