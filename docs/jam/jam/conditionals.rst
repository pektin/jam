.. _jam-conditionals:

Conditionals
############

Conditionals group a section of instructions and execute them depending on
whether a condition has been met or not.

Jam has two kinds of conditionals: A if conditional and a case conditional.

Syntax
======

::

    Conditional:
        <IfConditional>
        <CaseConditional>

    ElifClause:
        elif <Value> <newline> <InstructionSet>
        elif <Value> <newline> <InstructionSet> <newline> <ElifClause>

    IfConditional:
        if <Value> <newline> <InstructionSet> <newline> end
        if <Value> <newline> <InstructionSet> <newline> else <newline> <InstructionSet> <newline> end
        if <Value> <newline> <InstructionSet> <newline> <ElifClause> <newline> end
        if <Value> <newline> <InstructionSet> <newline> <ElifClause> <newline> else <newline> <InstructionSet> <newline> end

    IfConditionalValue:
        <Instruction> if <Value> <newline>
        <Instruction> if <Value> else <Instruction> <newline>

    WhenClause:
        when <Value> <newline> <InstructionSet>
        when <Value> <newline> <InstructionSet> <newline>  <WhenClause>

    CaseConditional:
        case <Value> <newline> <WhenClause> <newline> end
        case <Value> <newline> <WhenClause> <newline> else <newline> <InstructionSet> <newline> end
