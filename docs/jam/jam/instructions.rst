.. _jam-instructions:

Instructions
############

A instruction represents any single, top-level part of Jam's syntax.

Syntax
======

.. productionlist::
    Instruction: `Comment` | `Value` | `Assignment` | `FlowControl` | `Unittest`
    InstructionSet: `Instruction` [
                  : `InstructionSet`]

