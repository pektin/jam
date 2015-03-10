.. _jam-built-ins:

####################################
Built-in Functions, Values and Types
####################################

This document describes the functions, values and types built into the jam
language. Those which provide the base for which the rest of the standard
library is built upon.

Functions
=========

`print(*values:String[])`
    Outputs values to stdout

Values
======

`const nan:Real`
    Representation for floating point not-a-number value.

`const inf:Real`
    Representation for floating point infinity value. Use `-inf` for negative
    infinity.

`const null`
    A value for the absence of a value. Can only be assigned to
    variables that have a null-able type.

`const true:Bool`
    The boolean value of one

`const false:Bool`
    The boolean value of zero

Types
=====

`class Byte`
    A generic 8 bit piece of memory.

`class Bool`
    A one bit value. Has a range of 0 to 1.

Integer Types
-------------

Types specifically used to represent integer numbers.

`class Int`
    Generic integer class that dynamically expands to larger sizes when needed.
    This class is slower, but in return has no limit in size.

`class UInt`
    Generic unsigned integer class that dynamically expands to larger sizes
    when needed. This class is slower, but in return has not limit in size.

`class Int8`
    A 8 bit integer class. Has a range of −128 to 127.

`class UInt8`
    A 8 bit unsigned integer class. Has a range of 0 to 255.

`class Int16`
    A 16 bit integer class. Has a range of −32,768 to 32,767.

`class UInt16`
    A 16 bit unsigned integer class. Has a range of 0 to 65,535.

`class Int32`
    A 32 bit integer class. Has a range of −2,147,483,648 to 2,147,483,647.

`class UInt32`
    A 32 bit unsigned integer class. Has a range of 0 to 4,294,967,295.

`class Int64`
    A 64 bit integer class. Has a range of
    −9,223,372,036,854,775,808 to 9,223,372,036,854,775,807.

`class UInt64`
    A 64 bit unsigned integer class. Has a range of 0 to
    18,446,744,073,709,551,615.

`class Int128`
    A 128 bit integer class. Has a range of
    −170,141,183,460,469,231,731,687,303,715,884,105,728 to
    170,141,183,460,469,231,731,687,303,715,884,105,727.

`class UInt128`
    A 128 bit unsigned integer class. Has a range of 0 to
    340,282,366,920,938,463,463,374,607,431,768,211,455.

`class Size`
    A unsigned integer class, whose maximal value is always larger or equal to
    the maximal memory address of the running system.

Real Types
----------

Types specifically used to represent real numbers.

`class Real`
    Generic real number class with arbitrary precision.

`class Float16`
    A 16 bit IEEE floating point value.

`class Float32`
    A 32 bit IEEE floating point value.

`class Float64`
    A 32 bit IEEe floating point value.

Character Types
---------------

Types specifically used to represent characters in memory.

`class Char`
    A single 8 bit character.

`class String`
    A array of characters in a specific format. Supported formats are ASCII,
    UTF-8, UTF-16 and UTF-32.
