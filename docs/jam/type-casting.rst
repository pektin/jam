Type Casting
############

Type casting allows the programmer to convert between different types of
variables. Type casting is either implicit or explicit. Implicit casts are
inferred by the compiler, while explicit casts require the programmer to
explicitly perform the cast.

When a value is used in an invalid situation (eg. wrong type), all implicit
casts of that value are checked for a working variant. Only one implicit cast
may be a valid cast at any time.

Syntax
======

.. productionlist::
    TypeCast: `Value` "as" `Value`
