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

::

    Loop:
        <GenericLoop>
        <WhileLoop>
        <ForLoop>

    GenericLoop:
        loop <newline> <InstructionSet> <newline> end
        <Instruction> loop <newline>

    WhileLoop:
        while <Value> <newline> <InstructionSet> <newline> end
        <Instruction> while <Value> <newline>

    ForLoop:
        for <Variable> in <Value> <newline> <InstructionSet> <newline> end
        <Instruction> for <Variable> in <Value> <newline>
