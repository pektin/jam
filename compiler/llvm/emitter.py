from contextlib import contextmanager
from io import IOBase
from functools import partial

from ..lekvar.lekvar import *
from ..errors import *

# Temporary until LLVMType is replaced
LLVMMAP = {
    "String": "i8*",
    "Int": "i32",
    "Void": "void",
}

class Emitter:
    output = None
    stack = None
    current_stack = 0
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

    def write(self, string):
        # General write function
        if len(self.stack) > 0:
            self.writeLine(string)
        else:
            self.writeGlobal(string)

    def writeGlobal(self, string):
        # Write directly to the global output
        self.output.write(string)

    def writeLine(self, string):
        self.stack[-1] += string

    def writeStack(self, string):
        self.stack[self.current_stack] += string

    def writeMain(self, string):
        # Write directly to the main function
        self.main += string

    @property
    def in_line(self):
        # Return whether the current stack item is a line
        return self.current_stack < len(self.stack) - 1

    @contextmanager
    def lineWrite(self, entry=""):
        self.stack.append(entry)
        yield
        self.writeStack(self.stack.pop() + "\n")

    @contextmanager
    def stackWrite(self, entry=""):
        # Keep track of the current stack item
        previous_stack = self.current_stack
        self.current_stack = len(self.stack)

        self.stack.append(entry)
        yield
        self.writeGlobal(self.stack.pop() + "\n")
        # Revert to previous stack
        self.current_stack = previous_stack

    #
    # Name Generation
    #

    def resolveName(self, scope:Scope):
        # Resolves the name of a scope, starting with a extraneous .
        name = ""
        while scope.parent is not None:
            name += "." + scope.name
            scope = scope.parent
        return name

    temp_name_index = 0
    def getTempName(self, prefix):
        # Return a temporary, but unique name. Temporary names always start with temp
        name = "{}temp.{}".format(prefix, self.temp_name_index)
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

        self.writeMain("call void {}()\n".format(main.emit_data))

    def emitExternalFunction(self, function:ExternalFunction):
        function.emit_data = "@{}".format(function.external_name)

        # declare <return> @<name>(<arguments>)
        with self.stackWrite("declare "):

            self._emitType(function.return_type) # return

            self.write(" {}(".format(function.emit_data)) # name

            for index, type in enumerate(function.argument_types): # arguments
                if index > 0:
                    self.write(",")
                type.emit(self)
            self.write(")")

    @contextmanager
    def emitFunction(self, function:Function):
        function.emit_data = "@lekvar" + self.resolveName(function)

        # define <return> @<name>(<arguments>) {
        # <magic>
        # yield
        # label.return:
        # ret <return>
        # }

        with self.stackWrite("define "):
            not_void = function.return_type is not None

            if not_void:
                function.return_type.emit(self) # return
            else:
                self.write("void")

            self.write(" {}(".format(function.emit_data)) # name
            for index, argument in enumerate(function.arguments): # arguments
                if index > 0:
                    self.write(",")
                argument.emit_data = self.getTempName("%")
                argument.type.emit(self)
                self.write(" {}".format(argument.emit_data))
            self.write(") {\n")

            for argument in function.arguments: # magic
                name = argument.emit_data
                self._emitVariableAlloc(argument)
                def emit():
                    argument.type.emit(self)
                    self.write(" {}".format(name))
                self._emitVariableStore(argument, emit)

            if not_void: # only allocate return variable if function is not void
                self.write("%return = alloca ")
                function.return_type.emit(self)
                self.write("\n")
            self.write("\n")

            # Do other stuff
            yield
            # now finish off

            # fallthrough
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

    def emitFunctionValue(self, function:(Function, ExternalFunction)):
        # <return> @<name>
        if function.return_type is not None:
            function.return_type.emit(self) # return
        else:
            self.write("void")
        self.write(" {}".format(function.emit_data)) # @name

    def emitComment(self, comment:Comment):
        self.write(";{}\n".format(comment.contents))

    def emitLiteral(self, literal:Literal):
        # Emit a non-specific literal
        type = literal.resolveType()

        if not isinstance(type, LLVMType): #TODO: Get rid of LLVMType
            raise NotImplemented()

        if type.llvm_type == "String":
            # Create a global constant for it
            literal.emit_data = self.getTempName("@")
            # @<tempname> = internal constant [<size> x i8] c"<string>\00"
            self.writeGlobal("{} = internal constant [{} x i8] c\"{}\\00\"\n".format(literal.emit_data, len(literal.data) + 1, literal.data))
            # i8* getelementptr inbounds ([<size> x i8]* @<tempname>, i32 0, i32 0)
            self.write("i8* getelementptr inbounds ([{} x i8]* {}, i32 0, i32 0)".format(len(literal.data) + 1, literal.emit_data))
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
            #.. %<temp> = call <emit>
            call.emit_data = self.getTempName("%") # temp
            with self.lineWrite("{} = call ".format(call.emit_data)):
                emit()
            self._emitType(call.called.return_type)
            self.write(" {}".format(call.emit_data))

        else:
            # call <emit>
            with self.lineWrite("call "):
                emit()

    def emitReturn(self, ret:Return):
        if ret.parent.return_type is not None:
            with self.lineWrite("store "):
                ret.value.emit(self)
                self.write(", ")
                ret.parent.return_type.emit(self)
                self.write("* %return")
        self.write("br label %label.return\n")

    def _emitType(self, type:Type):
        # just map the mentioned type to a llvm type
        if type is None:
            self.write("void")
        else:
            type.emit(self)

    def emitLLVMType(self, type):
        self.write(LLVMMAP[type.llvm_type])

    def emitVariable(self, var:Variable):
        if var.emit_data is None:
            self._emitVariableAlloc(var)

        temp = self.getTempName("%")
        with self.lineWrite("{} = load ".format(temp)):
            var.type.emit(self)
            self.write("* {}".format(var.emit_data))
        var.type.emit(self)
        self.write(" {}".format(temp))

    def _emitVariableAlloc(self, var):
        var.emit_data = "%lekvar.{}".format(var.name)

        with self.lineWrite("{} = alloca ".format(var.emit_data)):
            var.type.emit(self)

    def emitAssignment(self, assignment):
        self._emitVariableStore(assignment.variable, partial(assignment.value.emit, self))

    def _emitVariableStore(self, var:Variable, store):
        if var.emit_data is None:
            self._emitVariableAlloc(var)

        with self.lineWrite("store "):
            store()
            self.write(",")
            var.type.emit(self)
            self.write("* {}".format(var.emit_data))
