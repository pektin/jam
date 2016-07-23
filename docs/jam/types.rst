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
other types, or include functionality from :doc:`traits`.

Metaclasses
===========

Since a core concept of Jam is that everything is an object, and objects have
types, classes must therefore also have a type. The type of a class is called a
metaclass. A metaclass is a class whose instances are classes, as such they
define the attributes and functionality of the class itself.

.. note::
    There is no syntax for metaclasses yet.

Syntax
======

.. productionlist::
    NullableType: `Type` ["?"]
    Type: `Identifier` | `ArrayType` | `AssociativeArrayType` | `Class` | `Enumeration` | `NullableType`
    InstanceVariable: `Variable` [ "=" `Value` ]
    ClassInstruction: `ClassConstructor` | `InstanceVariable` | `Assignment` | `Method` | `TypeCastDef` | `TemplateInclude`
    ClassInstructionSet: ( `ClassInstruction` \n )*
    ClassConstructorPrototype: "(" [ [`Argument` ","]* `Argument` ] ")"
    ClassConstructor: "new" `ClassConstructorPrototype` `InstructionSet` "end"
    ClassPrototype: `Identifier` ["?"] [ "(" `Type` ")" ]
    Class: [`Visibility`] "class" `ClassInstructionSet` "end"

.. note::

    The syntax for array and dictionary types is currently a place-holder

