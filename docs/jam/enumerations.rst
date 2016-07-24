Enumerations
############

An Enumeration (or enum for short) is a type whose only valid values are a set
of named constants. These constants themselves may be of any type, including the
enumeration itself.

Syntax
======

.. productionlist::
    EnumerationItem: `Identifier` [ "=>" `Value` ]
    EnumerationItems: ( `EnumerationItem` \n )*
    Enumeration: "enum" `Identifier` `EnumerationItems` "end"
