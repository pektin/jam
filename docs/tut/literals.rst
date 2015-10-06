Literals
########

Integers
========

Integers may be separated by an ``_`` for readability.

::

    # Standard representation
    299792458

    # Alternate representation
    299_792_458

Jam supports a variety of operations on integers.

::

    # Addition
    10 + 5 #=> 15

    # Subtraction
    10 - 5 #=> 5

    # Multiplication
    10 * 5 #=> 50

    # Integer Division
    10 // 5 #=> 2
    5 // 3 #=> 1

    # Division through implicit typecasting
    5 / 3 #=> 1.666_666_666..

    # Exponentiation
    4 ** 2 #=> 16

.. seealso::

    Language reference on :doc:`integer literals<../jam/literals/integers>`
    Language reference on :doc:`operations<../jam/operations>`

    Library reference on :doc:`numericals<../lib/builtins/types>`

Floating Point
==============

Floating point numbers have the same ``_`` support and support the same set of
operations.

::

    # Standard representation
    3.141592

    # Alternate representation
    3.141_592

    # Addition
    3.2 + 5.4 #=> 8.6

    # Subtraction
    3.2 - 5.4 #=> -2.2

    # Multiplication
    3.2 * 5.4 #=> 17.28

    # Division
    8.1 / 5.2 #=> 1.557_692_308

    # Exponentiation
    4.3 ** 2.1 #=> 21.3935_9435

.. seealso::

    Language reference on :doc:`float literals<../jam/literals/floats>`
    Language reference on :doc:`operations<../jam/operations>`

Booleans
========

The only valid boolean values are ``true`` and ``false``.

.. seealso::

    Language reference on :doc:`boolean literals<../jam/literals/booleans>`

    Library reference on :doc:`constants<../lib/builtins>`
