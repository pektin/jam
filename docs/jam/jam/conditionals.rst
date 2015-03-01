.. _jam-conditionals:

Conditionals
############

Conditionals group a section of instructions and execute them depending on
whether a condition has been met or not.

Jam has two kinds of conditionals: A if conditional and a case conditional.

Syntax
======

The if conditional starts with the if keyword (``if``) followed by a condition.
Optionally another condition may be checked if the previous one failed using
the else if keyword (``elif``) followed by that respective condition. The
conditional may optionally continue with a single else keyword (``else``)
and then terminate with an end keyword (``end``)

The case conditional starts with the case keyword (``case``) followed by
a single value. It may then continue with any number of when clauses, starting
with the when keyword (``when``) followed by a value that is checked for
equality against the case value. The conditional may contain an optional else
clause using the else keyword (``else``) for values that don't match. It ends
with the end keyword (``end``).
