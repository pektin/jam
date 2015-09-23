.. _jam-variables:

Variables
#########

Variables are temporary containers for values. A variable is created at the
point where it is first used. A variable may only have a single type that
must be compatible with all of the variable's usage.

Contrary to it's name, a variable may also be defined as constant/immutable. A
immutable variable may only be set to a single value, once. After the value has
been set, it may not be changed. Any member functions that mutate the value are
illegal.

Syntax
======

.. productionlist::
    Variable: [`Visibility`] ["const"] `Identifier` [":" `Type`]
