Conditionals
############

Conditionals group a section of instructions and execute them depending on
whether a condition has been met or not.

Jam has two kinds of conditionals: A "if" conditional and a "case" conditional.

Syntax
======

.. productionlist::
    Conditional: `IfConditional` | `CaseConditional`
    IfConditional: "if" `Value` `InstructionSet` ( `ElifConditional` | "end" )
    ElifConditional: "elif" `Value` `InstructionSet` ( `ElseConditional` | "end" )
    ElseConditional: "else" `InstructionSet` "end"
    CaseConditional: "case" `Value` `WhenConditional`* ( `ElseConditional` | "end" )
    WhenConditional: "when" `Value` `InstructionSet`
