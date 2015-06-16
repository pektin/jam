.. _basics-firststeps:

First Steps
###########

Variables and Constants
=======================

A large part of programming is the ability to read and write data. In Jam, 
:ref:`variables<jam-variables>` are theorertical containers which a programmer can use to store data. Each variable is associated with an :ref:`identifier<jam-identifiers>` and can be accessed by using that identifier. By definition, the data a variable holds can change during runtime, whereas a constant cannot be changed once it has been set.

The ``var`` keyword is used to denote a variable, without it, a constant is defined.

::

    # Defining a variable
    var count = 0 # This value will change

    # Defining a constant
    hours_per_day = 24 # This value will not
    

Values and data
===============

The :ref:`values<jam-values>` you can assign to variables can only be of a single type, however many different :ref:`types<jam-types>` exist. Depending on the purpose of the variable, different data types should be used.

The four basic types which are included in the builtin library are ``Int``,
``Float``, ``Boolean`` and ``String``

In brief, :ref:`Integers<jam-literals-integers>` are the set of Natural numbers, :ref:`Floats<jam-literals-floats>` are the set of Real numbers, :ref:`Booleans<jam-booleans>` are true or false values and :ref:`Strings<jam-literals-strings>` are collections of characters.

Integers and Floats can be either positive, negative or zero. 

As standard with other programming languages, assignment is done with the 
'=' operator.

::

    # Integers
    mass = 120
    var velocity = -15
    var counter = 0

    # Floats / Reals
    gravity = -9.8 # (m/s)
    pi = 3.145_926
    var probability = 0.5

    # Booleans
    var alive = true
    var dead = false

    # Strings
    var first_name = "Harrold"
    var last_name = `Banks`