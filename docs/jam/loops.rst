.. _jam-loops:

Loops
#####

Loops group a section of instructions and loops them. Jam has three kinds of
loops. A generic loops without a condition, a while loop with a simple condition
and a for loop for interaction.

While inside of a loop there are multiple other control structures that become
value. These are the break and continue statements.

Syntax
======

.. productionlist::
    Loop: `GenericLoop` | `WhileLoop` | `ForLoop`
    GenericLoop: "loop"
               :   `InstructionSet`
               : "end"
    WhileLoop: "while" `Value`
             :   `InstructionSet`
             : "end"
    ForLoop: "for" `Variable` "in" `Value`
           :   `InstructionSet`
           : "end"
