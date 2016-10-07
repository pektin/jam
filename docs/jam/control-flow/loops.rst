Loops
#####

Loops group a section of instructions and loops them. Jam has three kinds of
loops. A generic loops without a condition, a while loop with a simple condition
and a for loop for interaction.

While inside of a loop, the break and next statements can be used to control the
behaviour of the loop.

Syntax
======

.. productionlist::
    Break: "break"
    Next: "next"
    LoopInstruction: `Instruction` | `Break` | `Next`
    LoopInstructionSet: ( `LoopInstruction` \n )*
    Loop: `GenericLoop` | `WhileLoop` | `ForLoop`
    GenericLoop: "loop" `LoopInstructionSet` "end"
    WhileLoop: "while" `Value` `LoopInstructionSet` "end"
