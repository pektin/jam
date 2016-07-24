Constant
########

Constant is a modifier that enforces immutability of its value.

Syntax
======

.. productionlist::
    Constant: "const" `ModifierValue`

Example
-------
::

    const id = 4

    id = 3 # Error! Can't be changed

    name:const(String) = "Larissa"
    # Same as
    const name = "Larissa"
    # And
    name = const "Larissa"
