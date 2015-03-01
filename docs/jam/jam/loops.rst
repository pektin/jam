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

The generic loop starts with the loop keyword (``loop``) followed by a newline,
and ends with the end keyword (``end``), all looped instructions being
in-between.

The while loop starts with the while keyword (``while``) followed by a value
that is castable to the builtin ``Bool`` type. The loop ends with the end
keyword (``end``).

The for loop starts with the for keyword (``for``), followed by one or more
variable declarations, the in keyword (``in``) and a value as the target of
iteration. The loop ends with the end keyword (``end``).

The break statement is simply the break keyword (``break``) followed by a
newline.

The continue statement is simply the continue keyword (``continue``) followed by
a newline.
