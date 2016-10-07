Variables
#########

Variables are temporary containers for values. The value stored in the container
may only be of a single type, for each variable. This makes it easier to reason
about what a variable can/is storing at any point in time.

Variable Inference
==================

Variables do not require any special syntax to create. Simply assign to an
unused :doc:`identifiers` and a new variable will be created in the current
scope.

Variables are also inferred through control flow blocks, if they are guaranteed
to exist in all execution paths.

Example
-------
::

    if condition
      foo = 2
    else
      foo = 4
    end

    puts(foo) # foo is inferred into this context

Type Inference
==============

The type of a variable is inferred by all :doc:`assignments` to it. If a
variable is assigned multiple values that have a common supertype, the variable
is inferred to be of that supertype. Type inference can be overriden using the
:doc:`"Type of" operation<operations>`.
