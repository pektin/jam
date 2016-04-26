Booleans
########

A boolean represents a value that can only be in two states, either true or
false. Booleans are of the builtin type ``Bool``.

Syntax
======

.. productionlist::
    Boolean: "true" | "false"

Examples
--------
::

    # Boolean variables used in a conditional block
    state = true

    if state == true
      puts("This will print\n")
    else
      puts("This will not\n")
    end


    # Boolean value used in a conditional block
    if true
      puts("This will always print\n")
    else
      puts("This will never print\n")
    end
