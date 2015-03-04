.. _jam-booleans:

Booleans
########

A boolean represents a value that can only be in two states, either true or
false. Booleans are of the builtin type ``Bool``.

Syntax
======

.. productionlist::
    Booleans: "true" | "false"

Example
-------

::

    # Print: bar
    if false
        print("foo")
    elif true
        print("bar")
    end
