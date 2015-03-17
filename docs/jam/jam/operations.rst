.. _jam-operations:

Operations
##########

Jam supports a large set of standard operations. These operations link directly
to methods defining their behaviour.

There are two kinds of operators, binary and unary. Binary operations require
exactly two values, while unary require exactly one.

Operators
---------

=============== =============================
Binary Operator Meaning
=============== =============================
``==``          Equality
``!=``          Inverse Equality
``<``           Smaller than
``<=``          Smaller than or equal to
``>``           Larger than
``>=``          Larger than or equal to
``is``          Identity Equivalence
``!is``         Inverse Identity Equivalence
``+``           Addition
``-``           Subtraction
``*``           Multiplication
``/``           Division
``//``          Integer Division
``**``          Exponentiation
``%``           Modulo
``in``          Containment
``&&``          Logical And
``||``          Logical Or
``&``           Bitwise And
``|``           Bitwise Or
``^``           Bitwise Exclusive Or
=============== =============================

============== ===============
Unary Operator Meaning
============== ===============
``!``          Logical Not
``~``          Bitwise Inverse
============== ===============

Syntax
======

.. productionlist::
    ComparisonOperator: "!=" | "==" | "<" | "<=" | ">" | ">=" | "is" | "!is"
    ComparisonOperation: `Value` [`ComparisonOperator` `ComparisonOperation`]
    BinaryOperator: "%" | "^" | "&" | "&&" | "*" | "**" | "-" | "+" | "|" | "||" | "/" | "//" | "in"
    BinaryOperation: (`Value` `BinaryOperator` `Value`) | `ComparisonOperation`
    UnaryOperator: "~" | "!"
    UnaryOperation: [`UnaryOperator`] `Value`
    Operation: `UnaryOperation` | `BinaryOperation`
