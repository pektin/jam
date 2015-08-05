.. _tutorial-basics-literals:

Literals
########

Integers
========

Integers directly in source code are of the generic ``Int`` type.

::

    # The number 192
    192

Other integer types also exist:

=========== ====================================
Type        Description
=========== ====================================
``Int``     Grows/shrinks in size when required.
``Int8``    8 bit signed integer
``Int16``   16 bit signed integer
``Int32``   32 bit signed integer
``Int64``   64 bit signed integer
``Int128``  128 bit signed integer
``UInt``    Unsigned version of ``Int``
``UInt8``   8 bit unsigned integer
``UInt16``  16 bit unsigned integer
``UInt32``  32 bit unsigned integer
``UInt64``  64 bit unsigned integer
``UInt128`` 128 bit unsigned integer
=========== ====================================

For literals of a type other than ``Int`` use casting:

::

    127 as Int8

    -52 as UInt # Invalid!

Large numbers are difficult to read, so jam allows for separating groups of
digits by an ``_``:

::

    # Standard representation
    299792458

    # Alternate representation
    299_792_458

The following operations are supported by integers:

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

    Language reference on :ref:`integer literals<jam-literals-integers>`
    Language reference on :ref:`operations<jam-operations>`

    Library reference on :ref:`numericals<jam-builtins-numerical>`

Floats
======

In the same way as integers, real numbers are of the type ``Float`` by default.
The other possible types are:

============ =============================
Type         Description
============ =============================
``Float``    Arbitrary precision float
``Float16``  16 bit signed float
``Float32``  32 bit signed float
``Float64``  64 bit signed float
``UFloat``   Unsigned version of ``Float``
``UFloat16`` 16 bit unsigned float
``UFloat32`` 32 bit unsigned float
``UFloat64`` 64 bit unsigned float
============ =============================

::

    # Standard representation
    3.141592

    # Alternate representation
    3.141_592

The following operations apply to floats:

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

.. seealso::

    Language reference on :ref:`float literals<jam-literals-floats>`
    Language reference on :ref:`operations<jam-operations>`

    Library reference on :ref:`numericals<jam-builtins-numerical>`

Booleans
========

Booleans are of the type ``Bool``. The only valid literals are ``true`` and
``false``.

.. seealso::

    Language reference on :ref:`boolean literals<jam-literals-booleans>`

    Library reference on :ref:`constants<jam-builtins-constants>`
