Variables
#########

Variables are temporary containers for values. A variable is created at the
point where it is first used. A variable may only have a single type that must
be compatible with all of the variable's usage.

Contrary to it's name, a variable may also be defined as constant/immutable. A
immutable variable may only be set to a single value, once. After the value has
been set, it may not be changed. Any member functions that mutate the value are
illegal.

Type Inference
==============

The type of a variable may be declared any number of times. If the type is
declared more than once, each declaration has to be compatible. If no type
declaration is given, it is inferred by the compiler.

The type of a variable is inferred by all :doc:`assignments` to it. If a
variable is assigned a value of a type and is later assigned a value of a
supertype of the initial assignment, the variables type is inferred to the
supertype.

Syntax
======

.. productionlist::
    Variable: [`Visibility`] ["const"] `Identifier` [":" `Type`]
