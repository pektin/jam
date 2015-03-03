.. _jam-types:

Types
#####

Types describe how values behave and what they are made of.

Type Inference
==============

When a type is not specified, the compiler has to infer it.

For a variable, the type is determined by all assignments to that variable.
When a variable is assigned a value of a superset type, the type of the variable
changes to the superset. A variable cannot be assigned any value of a type that
is incompatible.

For a argument, the type is determined by every action involving that argument.
From this it builds a "type expectation" that is used at compile time to check
whether arguments are valid.

Nullability
===========

A type may be explicitly marked as nullable, meaning that the ``null`` value may
be assigned to it. A nullable type does not allow member access unless the value
is checked for ``null``, or is cast to the type's non-nullable counterpart.

A type may be marked as nullable either at definition or declaration.

Syntax
======

.. productionlist::
    Type: (`Identifier` | `ArrayType` | `DictType` | `Class`)["?"]
    ArrayType: `Type` "[" ( [`Integer`] "," )* [`Integer`] "]"
    DictType: "{" `Type` "->" `Type` "}"
    InstanceVariable: `Variable` ["=" `Value`]
    ClassInstructionSet: (`InstanceVariable` | `Assignment` | `Method` | `TypeCastDef`
                       : )*
    Class: "class" `Identifier` ["?"] [ "(" `Identifier` ")" ]
         :     `ClassInstructionSet`
         : "end"

.. note::

    The syntax for array and dictionary types is currently a place-holder

