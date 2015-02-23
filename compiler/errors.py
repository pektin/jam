class SyntaxError(Exception):
    pass

class SemanticError(Exception):
    pass

class TypeError(SemanticError):
    pass

class ValueError(SemanticError):
    pass

class AmbiguetyError(SemanticError):
    pass

class MissingReferenceError(SemanticError):
    pass

class InternalError(Exception):
    pass

class NotImplemented(Exception):
    pass
