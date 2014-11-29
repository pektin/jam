
def err(message:str):
    raise Exception(message)

#
# Base Structures
#

class Variable:
    def __init__(self, name:str, mutable:bool,
                 type = None):
        sekf.name = name
        self.mutable = mutable
        self.type = type

class Scope:
    parent = None
    name = None
    instructions = []
    variables = {}
    children = {}
    varified = False

    def verify(self):
        for instruction in self.instructions:
            instruction.verify(self)

        for child in self.children:
            if not child.verified:
                child.verify()

    def resolveReference(self, name:str):
        occurrences = self._resolveReference(name)

        if len(occurrences) < 1:
            err("Missing reference")
        if len(occurrences) > 1:
            err("Ambiguous reference")

        return occurrences[0]

    def _resolveReference(self, name:str):
        occurrences = []
        if self.parent is None:
            occurrences = self.parent._resolveReference(name)

        return occurrences + self.resolveLocalReference(name)

    def resolveLocalReference(self, name:str):
        if name in self.variables:
            return [self.variables[name]]
        return []

class Value:
    def resolveType(self, scope:Scope):
        err("Internal Error (Value)")

class Instruction:
    def verify(self, scope:Scope):
        err("Internal Error (Instruction)")

#
# Scope Structures
#

class Function(Scope):
    def __init__(self, name:str, parameters:[Variable], instructions:[Instruction], variables:{str:Variable},
                 return_types:[] = None, pure:bool = None, inline:bool = None):
        self.name = name
        self.parameters = parameters
        self.instructions = instructions
        self.return_types = return_types
        self.pure = pure
        self.inline = inline

    def resolveLocalReference(self, name:str):
        occurrences = []
        if name in self.variables:
            occurrences.append(self.variables[name])

        for parameter in self.parameters:
            if parameter.name == name:
                occurrences.append(parameter)
        return occurrences

class Module(Scope):
    def __init__(self, name:str, instructions:[Instruction], variables:{str:Variable}, children:{str:[Scope]}):
        self.name = name
        self.instructions = instructions
        self.variables = variables
        self.children = children

#
# Value Structures
#

class Literal(Value):
    def __init__(self, type, data:bytes):
        self.type = type
        self.data = data

    def resolveType(self, scope:Scope):
        return [self.type]

class Reference(Value):
    def __init__(self, name:str):
        self.name = name

    def resolveType(self, scope:Scope):
        variable = scope.resolveReference(scope, self.name)

        # Probably avoidable
        if variable.type is None:
            err("Could not infer variable type")
        return [variable.type]

class Call(Value):
    def __init__(self, function:Function, parameters:[Value]):
        self.function = function
        self.parameters = parameters

    def resolveType(self, scope:Scope):
        if not self.function.verified:
            self.function.verify()
        return self.function.return_types

#
# Instruction Structures
#

class Assignment(Instruction):
    def __init__(self, variables:[[str]], values:[Value]):
        self.variables = variables
        self.values = values

    def verify(self, scope:Scope):
        # Get assigned types
        types = sum((value.resolveType(scope) for value in self.values), [])

        for index, variables in enumerate(self.variables):
            # Sanity Check
            if len(variables) != len(types):
                err("Mismatched assignment")

            for reference in variables:
                variable = scope.resolveReference(scope, reference)

                # Infer type
                if variable.type is None:
                    variable.type = types[index]
                # Type Check (Replace)
                elif variable.type is not types[index]:
                    err("Type mismatch")

class Return(Instruction):
    def __init__(self, values:[Value]):
        self.values = values

    def verify(self, scope:Scope):
        # Sanity Check
        if not isinstance(scope, Function):
            err("Internal Error (Invalid Generation)")

        # Get types
        types = [value.resolveType(scope)
                 for index, value in enumerate(self.values)]

        # Infer Return Types
        if scope.return_types is None:
            scope.return_types = types
        else:
            if len(types) != len(scope.return_types):
                err("Mismatched return types")

            for index in range(len(types)):
                if types[index] is not scope.return_types[index]:
                    err("Mismatched return return_types")
