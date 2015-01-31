.. _jam-built-ins:

####################################
Built-in Functions, Values and Types
####################################

This document describes the functions, values and types built into the jam
language. Those which provide the base for which the rest of the standard
library is built upon.

Functions
=========

`puts(String)`

Values
======

`nan:Float`
    Representation for floating point not-a-number value.

`inf:Float`
    Representation for floating point infinity value. Use `-inf` for negative
    infinity.

`null`
    A value for the absence of a value. Can only be assigned to
    variables that have a null-able type.

Types
=====

`type Byte`
    A generic 8 bit value

Character Types
---------------

`type Char`
    A single character

`type String`
    An array of characters

Floating point Types
--------------------

`type Half`
    A 16bit Floating point value

`type Float`
    A 32bit Floating point value

`type Double`
    A 64bit Floating point value

Integer Types
-------------

`type Short`
    A 16bit signed Integer value

`type Int`
    A 32bit signed Integer value

`type Long`
    A 64bit signed Integer value
