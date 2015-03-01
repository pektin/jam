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

Syntax
======

::

    Type:
        <Identifier>
        <ArrayType>
        <DictType>
        <Class>

    ArrayTypeLength:
        <Integer>
        <Integer> , <ArrayTypeLength>
        , <ArrayTypeLength>

    ArrayType:
        <Type> [ ]
        <Type> [ <ArrayTypeLength> ]

    DictType:
        { <Type> -> <Type> }

    ClassInstruction:
        <Variable>
        <Assignment>
        <Method>
        <TypeCastDef>

    ClassInstructionSet:
        <ClassInstruction>
        <ClassInstruction> <newline> <ClassInstructionSet>

    Class:
        class <Identifier> <newline> <ClassInstructionSet> <newline> end
        class <Identifier>(<Identifier>) <newline> <ClassInstructionSet> <newline> end

