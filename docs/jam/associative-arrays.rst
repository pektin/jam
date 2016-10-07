Associative Arrays
##################

Associative arrays, also known as dictionaries and hash tables/maps, are a
collection of key-value pairs, with keys being unique.

Syntax
======

.. productionlist::
    AssociativeArrayValue: "{" `AssociativeArrayElement` ( `ArraySeparator` `AssociativeArrayElement` )* "}"
    AssociativeArrayElement: `Value` "=>" `Value`
