import logging
from contextlib import contextmanager

from ..errors import CompilerError

from .state import State
from .core import Context, Object, BoundObject, SoftScope, Scope, Type
from .module import Module
from .closure import Closure, ClosedLink, ClosedTarget
from .function import Function, FunctionType, FunctionInstance, Return
from .external_function import ExternalFunction
from .call import Call
from .method import Method, MethodType, MethodInstance
from .links import Link, BoundLink, ContextLink, Attribute
from .identifier import Identifier
from .modifiers import Constant, Reference
from .variable import Variable
from .assignment import Assignment
from .class_ import Class, Constructor
from .dependent import DependentObject, DependentTarget
from .literal import Literal
from .branches import Loop, Break, Branch
from . import util
from . import dependent

def _verify(source, frontend, logger = logging.getLogger()):
    logger.info("Parsing")
    module = frontend.parse(source, logger)

    logger.info("Verifying")
    verify(module, logger)

    return module

def compile(source, frontend, backend, logger = logging.getLogger(), opt_level = 0):
    module = _verify(source, frontend, logger)

    logger.info("Generating Code")
    return backend.emit(module, logger, opt_level)

def run(source, frontend, backend, logger = logging.getLogger(), opt_level = 0):
    module = _verify(source, frontend, logger)

    logger.info("Running")
    return backend.run(module)

def verify(module:Module, logger = logging.getLogger()):
    # Set up the initial state before verifying
    State.init(logger.getChild("lekvar"))

    State.logger.info(module.context)

    try:
        module.verify()
    except CompilerError as e:
        e.format()
        raise e

@contextmanager
def use(frontend, backend, logger = logging.getLogger()):
    with useFrontend(frontend, logger), useBackend(backend, logger):
        yield

@contextmanager
def useFrontend(frontend, logger = logging.getLogger()):
    builtins = frontend.builtins(logger)
    # Hack backend into frontend builtins
    builtins.context.addChild(DependentObject(builtins, "_builtins"))
    verify(builtins)

    try:
        old_builtins = State.builtins
        State.builtins = builtins
        yield
    finally:
        State.builtins = old_builtins

@contextmanager
def useBackend(backend, logger = logging.getLogger()):
    backend_builtins = backend.builtins(logger)
    builtins = State.builtins.context["_builtins"]

    with dependent.target([(builtins, backend_builtins)], False):
        yield
