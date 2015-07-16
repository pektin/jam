from ..errors import *
from .core import Context, Object, BoundObject, Type

# A dependent object is a collector for behaviour
# Initially the object is used like any other, creating dependencies
# Later a object can be chosen to "replace" the dependent object,
# Which is then checked for all the dependencies,
# This is similar to templating, but much more powerful and less context
# dependent.
class DependentObject(Type):
    # The target object which which to replace the dependent object
    target = None

    # Dependencies
    dependent_type = None
    dependent_calls = None
    dependent_context = None
    dependent_local_context = None
    dependent_instance_context = None
    dependent_instance_calls = None
    dependent_types = None

    def __init__(self, name:str = None, tokens = None):
        super().__init__(name or "", tokens)

        self.dependent_calls = dict()
        self.dependent_instance_calls = dict()
        self.dependent_types = set()

    def copy(self):
        raise InternalError("Not Implemented")

    def verify(self):
        pass

    # alias to the target if it exists
    def resolveValue(self):
        if self.target is not None:
            return self.target
        return self

    # Check whether an object matches the dependencies of this object
    def resolveDependency(self, target):
        if self.dependent_type is not None:
            self.dependent_type.resolveDependency(target.resolveType())

        #TODO: Handle errors
        for call in self.dependent_calls:
            self.dependent_calls[call].resolveDependency(target.resolveCall(call))

        if self.dependent_context is not None:
            self.dependent_context.resolveDependency(target.context)

        if self.dependent_local_context is not None:
            self.dependent_local_context.resolveDependency(target.local_context)

        if self.dependent_instance_context is not None:
            self.dependent_instance_context.resolveDependency(target.instance_context)

        for call in self.dependent_instance_calls:
            self.dependent_instance_calls[call].resolveDependency(target.resolveCall(call))

        for type in self.dependent_types:
            if not target.checkCompatibility(type):
                raise DependencyError("Dependent target type is not compatible with {}".format(type), target.tokens)

    # Create and cache dependencies for standard object functionality

    def resolveType(self):
        if self.dependent_type is None:
            self.dependent_type = DependentObject()
        return self.dependent_type

    def resolveCall(self, call):
        if call not in self.dependent_calls:
            self.dependent_calls[call] = DependentObject()
        return self.dependent_calls[call]

    @property
    def context(self):
        if self.dependent_context is None:
            self.dependent_context = DependentContext()
        return self.dependent_context

    @property
    def local_context(self):
        if self.dependent_local_context is None:
            self.dependent_local_context = DependentContext()
        return self.dependent_local_context

    @property
    def instance_context(self):
        if self.dependent_instance_context is None:
            self.dependent_instance_context = DependentContext()
        return self.dependent_instance_context

    def resolveInstanceCall(self, call):
        if call not in self.dependent_instance_calls:
            self.dependent_instance_calls[call] = DependentContext()
        return self.dependent_instance_calls[call]

    def checkCompatibility(self, other:Type):
        self.dependent_types.add(other)
        return True

    def __repr__(self):
        if self.target is None:
            return "{}".format(self.__class__.__name__)
        else:
            return "{} as {}".format(self.__class__.__name__, self.target)

# The dependent context compliments the dependent object with the creation
# of dependencies for contexts.
class DependentContext(Context):
    def __init__(self, scope:BoundObject):
        super().__init__(scope, [])

    def __contains__(self, name:str):
        return True

    def __getitem__(self, name:str):
        if name not in self.children:
            self.addChild(DependentObject(name))
        return self.children[name]

    def __setitem__(self, name:str, value:BoundObject):
        raise InternalError("Not Implemented.")

    def resolveDependency(self, target:Context):
        # Check whether target has the same children
        for name in self.children:
            if name not in target.children:
                raise DependencyError("Dependent target context does not have attribute {}".format(name), target.scope.tokens)

            # Resolve dependency for child
            self[name].resolveDependency(target[name])
