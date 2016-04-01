import logging
from contextlib import contextmanager

from ..errors import CompilerError

from .state import State
from .core import Context, Object, BoundObject, SoftScope, Scope, Type
from .module import Module
from .function import Function, FunctionType, Return, ClosedLink
from .external_function import ExternalFunction
from .call import Call
from .method import Method, MethodType, MethodInstance
from .links import Link, BoundLink, Identifier, Attribute
from .modifiers import Constant, Reference
from .variable import Variable
from .assignment import Assignment
from .class_ import Class, Constructor
from .dependent import DependentObject, DependentTarget
from .literal import Literal
from .branches import Loop, Break, Branch
from . import util

def compile(source, frontend, backend, logger = logging.getLogger(), opt_level = 0):
    module = frontend.parse(source, logger)

    builtins = frontend.builtins(logger)
    # Hack backend builtins into frontend builtins
    builtins.context.addChild(backend.builtins(logger))

    verify(module, builtins, logger)

    return backend.emit(module, logger, opt_level)

def verify(module:Module, builtin:Module, logger = logging.getLogger()):
    # Set up the initial state before verifying
    State.init(builtin, logger.getChild("lekvar"))

    State.logger.info(module.context)

    try:
        module.verify()
    except CompilerError as e:
        e.format()
        raise e
