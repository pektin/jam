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

Order of Operations
-------------------

.. todo::
    Complete this description

For Binary Operations, Order of Operations is ranked using the PEDMAS system.
The operations in descending rank order are Parenthesis, Exponents, Division,
Multiplication, Addition, Subtraction. A group of operations of the same rank
will be executed from left to right.

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

Examples
========

Mathematical
------------

::

    # Addition
    size = 5 + 3 #=> 8
    total_volume = 6.8 + 2.3 #=> 9.1

    # Subtraction
    size = 3 - 5 #=> -2
    total_volume = 6.8 - 2.3 #=> 4.5

    # Multiplication
    area = 5 * 3 #=> 15
    depreciation_rate = 2 * -5.3 #=> -10.6

    # Division
    ratio = 5.0 / 2.0 #=> 2.5

    # Integer Division
    portion = 10 // 3 #=> 3
    half = 8 // 4 #=> 2

    # Exponentiation
    y_coord = x_coord**2
    decay_rate = 2**-2 #=> 0.25

    # Modulo
    TODO

Equivalence
-----------

::

    # Equality
    if num_sides == 4
        print("Shape is a square")
    end

    # Inverse Equality
    if num_eyes != 2
        print("Not human")
    end


Relational
----------

::

    # Smaller than
    while count < 10
        print(count)
        count += 1
    end

    # Smaller than or equal to
    #TODO

    # Larger than
    if score > high_score
        high_score = score
    end

    # Larger than or equal to
    #TODO


Identity
--------

::

    # Identity Equivalence
    #TODO

    # Inverse Identity Equivalence
    #TODO

Containment
-----------

::

    #TODO


Logical
-------

::

    # And
    if total_score >= 50 && final_exam_score >= 50
        return true #passed
    else
        return false #failed
    end

    # Or
    if rank > 5 || difficulty_setting == 2
        difficulty = 2
    end

    # Logical Not
    #TODO


Bitwise
-------

::

    # And
    #TODO

    # Or
    #TODO

    # Exclusive Or
    #TODO

    # Bitwise Inverse
    TODO
