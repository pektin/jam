.. _jam-type-casting:

Type Casting
############

Type casting allows the programmer to convert between different types of
variables. Type casting is either implicit or explicit. Implicit casts are
inferred by the compiler, while explicit casts require the programmer to specify
the cast.

Syntax
======

::

    TypeCast:
        <ExplicitCast>

    ExplicitCast:
        <Value> as <Type>

    TypeCastDef:
        <ImplicitCastDef>
        <ExplicitCastDef>

    ImplicitCastDef:
        def self : <Type> <newline> <InstructionSet> <newline> end

    ExplicitCastDef:
        def self as <Type> <newline> <InstructionSet> <newline> end
