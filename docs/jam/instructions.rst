Instructions
############

A instruction represents any single, top-level part of Jam's syntax.

Syntax
======

.. productionlist::
    Instruction: `Comment` | `Value` | `Assignment` | `FlowControl` | `Import` | `Unittest`
    InstructionSet: ( `Instruction` \n )*
