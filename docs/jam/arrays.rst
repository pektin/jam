.. _jam-arrays:

Arrays
######

Arrays are a zero indexed, ordered set of values as a singular value. Arrays
can either be dynamic, where the number of elements may change, or static, where
it may not.

Array values may be created either by defining separate elements individually,
or by defining one element over a range of indecies. Mixing both is also valid.

Types
=====

The type of an array is identical to normal array values, except that values are
replaced by types.

Syntax
======

.. productionlist::
    ArrayType: "[" `Type` [ ";" `Integer` ] "]"
    ArrayValue: "[" `ArrayElement` (( "," |
              : ) `ArrayElement`)* "]"
    ArrayElement: `Value` [";" `Integer`]
