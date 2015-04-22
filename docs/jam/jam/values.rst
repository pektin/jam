.. _jam-values:

Values
######

A value represents a piece of data in memory. Every value has a type, which
describes that values representation in memory. Values are an abstract concept
which will be used by other parts of the language.

Values may be used as input for instructions or other values. Values may have
side effects.

.. productionlist::
    Value: `Identifier` | `Literal` | `Method` | `Class` | `TypeCast` | `Attribute` | `Operation` | `Template` | `ArrayValue`
