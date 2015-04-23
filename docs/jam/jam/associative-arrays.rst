.. _jam-associative-arrays:

Associative Arrays
##################

Associative arrays, also known as dictionaries and hash tables, are a
collection of key-value pairs, with keys being unique.

Associative arrays are created through a set of key-value pairs.

Types
=====

The type of an associative array is defined in the same way it's values are,
through a single map of a type to another.

Syntax
======

.. productionlist::
    AssociativeArrayType: "{" `Type` "->" `Type` "}"
    AssociativeArrayValue: "{" `AssociativeArrayElement` (("," |
                         : ) `AssociativeArrayElement`)* "}"
    AssociativeArrayElement: `Value` "->" `Value`
