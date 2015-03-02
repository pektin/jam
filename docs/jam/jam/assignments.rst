.. _jam-assignments:

Assignments
###########

Assignments are used to directly store values in variables. A single assignment
may involve any number of values and variables, however the numbers must match
up. Two values can be assigned to two variables, or to three groups of two
variables, but three values cannot be assigned to two variables.

Syntax
======

.. productionlist::
    AssignmentVars: [`Variable` ","]* `Variable`
    Assignment: [`AssignmentVars` "="]* `AssignmentVars` "=" [`Value` ","]* `Value`
