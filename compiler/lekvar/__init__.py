import logging

from .state import State
from .core import Context, Object, BoundObject, Type
from .module import Module, ModuleType
from .function import Function, FunctionType, Return
from .external_function import ExternalFunction
from .call import Call
from .method import Method, MethodType
from .links import Reference, Attribute
from .variable import Variable, Assignment
from .class_ import Class, Constructor
from .dependent import DependentType
from .literal import Literal
from .branches import Loop, Break, Branch
from .comment import Comment

def verify(module:Module, builtin:Module, logger = logging.getLogger()):
    # Set up the initial state before verifying
    State.init(builtin, logger.getChild("lekvar"))

    State.logger.info(module.context)

    module.verify()
