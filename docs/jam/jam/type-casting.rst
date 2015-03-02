.. _jam-type-casting:

Type Casting
############

Type casting allows the programmer to convert between different types of
variables. Type casting is either implicit or explicit. Implicit casts are
inferred by the compiler, while explicit casts require the programmer to specify
the cast.

When an operation is done to a value all implicit casts are checked for that
same operation. Although the direct type of the value takes precedence, having
ambiguity between implicitly cast types is invalid.

When a value is passed to a function, the value may be implicitly cast to the
type of the respective argument if required.

Syntax
======

.. productionlist::
    TypeCast: `Value` "as" `Type`
    TypeCastDef: `ImplicitCastDef` | `ExplicitCastDef`
    ImplicitCastDef: "def" "self" ":" `Type`
                   :     `InstructionSet`
                   : "end"
    ExplicitCastDef: "def" "self" "as" `Type`
