.. _tut-variables:

Variables
#########

Variables are mutable containers for values. Because Jam is statically typed,
every variables has exactly one type. It is however never necessary to
explicitly specify the type of a variable as the compiler will infer one.

::

    # Explicitly declare `x` as an integer and assign 12
    x:Int = 12

    # Let the compiler infer the type of `greeting` to be  `String`
    greeting = "Hello"

.. note::

    Although by design a variable's type never needs to be defined, this is not
    the case yet.

Jam does not differentiate between a declaration and an assignment, thus
variables are implicitly declared on their first assignment. This holds inside
local scopes as well.

::

    # Declaration and assignment
    a = 9
    # Just an assignment
    a = 4

    # Works for local scopes
    # `b` does not have to be declared before the if block
    if some_condition
      b = "yes"
    else
      b = "no"
    end
    puts(b)

A variable's type may not change. Therefore assignment a value not compatible
with its type is not allowed.

::

    a = 9
    # TypeError:
    # Cannot assign `"Hello World"` of type String to variable `a` of type `Int`
    a = "String"
