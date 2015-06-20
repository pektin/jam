.. _basics-literals:

Literals
###############

Integers
========
A whole number of the built-in type ``Int``

Signed Integers : ``Int8``, ``Int16``, ``Int32``, ``Int64``, ``Int128``

Unsigned Integers : ``UInt8``, ``UInt16``, ``UInt32``, ``UInt64``, ``UInt128``

By default, Integers are Signed Generic Int. The Generic ``Int`` class can 
represent infinitely large numbers, limited only by physical memory.

::
    
    # Standard representation
    299792458

    # Alternate representation
    299_792_458


Operations
----------
The following standard Integer operations apply

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


See more
--------
:ref:`Integer language reference<jam-literals-integers>`

:ref:`Integer library reference<jam-literals-integers>`

Floats
========
A Real number of built-in type ``Float``

Signed Floats : ``Float32``, ``Float64``

Unsigned Floats : ``UFloat32``, ``UFloat32``

By default, Floats are Signed arbitrary precision. The generic ``Float`` class
can represent infinitely large or small numbers, limited only by physical
memory.

::
    
    # Standard representation
    3.141592

    # Alternate representation
    3.141_592


Operations
----------
The following standard Integer operations apply

::
    
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


See more
--------
:ref:`Float language reference<jam-literals-floats>`

:ref:`Float library reference<jam-literals-floats>`


Boolean
========
``true`` or ``false`` values. Booleans are of the built-in type ``Bool``

See more
--------
:ref:`Boolean language reference<jam-literals-boolean>`

:ref:`Boolean library reference<jam-literals-boolean>`














