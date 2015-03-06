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

Examples
--------

Single Variable
~~~~~~~~~~~~~~~~~~~~
::

    width = 5
    length = 10
    height = 6

    futureState = currentState = true


Multi Variable
~~~~~~~~~~~~~~~~~~~
::
    
    # Defines a Rectangular Prism
    width, length, height = 5, 10, 6


    # The upperLimit is set to the currentPosition, then 
    # The currentPosition is set to the lowerLimit
    upperLimit, currentPosition = currentPosition, lowerLimit


    # velocity is equal to speed which is equal to 55.25, and
    # mass is equal to weight which is 100 
    velocity, mass = speed, weight = 55.25, 100




