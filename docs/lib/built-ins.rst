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

`type String`
    An array of characters
