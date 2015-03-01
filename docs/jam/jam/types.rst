.. _jam-types:

Types
#####

Types describe how values behave and what they are made of.

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
        <Instruction>
        <Variable>

    ClassInstructionSet:
        <ClassInstruction>
        <ClassInstruction> <newline> <ClassInstructionSet>

    Class:
        class <Identifier> <newline> <ClassInstructionSet> <newline> end
        class <Identifier>(<Identifier>) <newline> <ClassInstructionSet> <newline> end

