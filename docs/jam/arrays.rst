Arrays
######

Arrays are a zero indexed, ordered set of values as a singular value. Arrays
can either be dynamic, where the number of elements may change, or static, where
it may not.

Array values may be created by defining separate elements individually, or
inclusively by defining one element over a range of indices.

Syntax
======

.. productionlist::
    ArraySeparator: "," | \n
    ArrayValue: "[" `ArrayElement` ( `ArraySeparator` `ArrayElement` )* "]"
    ArrayElement: `Value` [ ";" `Integer` ]
