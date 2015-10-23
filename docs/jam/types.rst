Types
#####

Types describe how values behave and what they are made of.

Nullability
===========

A type may be explicitly marked as nullable, meaning that the ``null`` value may
be assigned to it. A nullable type does not allow member access unless the value
is checked for ``null``, or is cast to the type's non-nullable counterpart.

A type may be marked as nullable either at definition or declaration.

Classes
=======

A class is a user defined type. A class may have instance fields and methods,
which can be accessed as attributes. It may also inherit functionality from
other types, or include functionality from templates.

Syntax
======

.. productionlist::
    Type: (`Identifier` | `ArrayType` | `AssociativeArrayType` | `Class` | `Enumeration`)["?"]
    InstanceVariable: `Variable` ["=" `Value`]
    ClassInstructionSet:  (`ClassConstructor` | `InstanceVariable` | `Assignment` | `Method` | `TypeCastDef` | `TemplateInclude`
                       : )*
    ClassConstructor: "new" [`Identifier`] "(" [ [`Argument` ","]* `Argument` ] ")"
                    :     `InstructionSet`
                    : "end"
    Class: [`Visibility`] "class" `Identifier` ["?"] [ "(" `Identifier` ")" ]
         :   `ClassInstructionSet`
         : "end"

.. note::

    The syntax for array and dictionary types is currently a place-holder

