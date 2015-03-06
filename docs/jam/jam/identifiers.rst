.. _jam-identifiers:

Identifiers
###########

Identifiers are used to identify values in Jam. When an identifier is used by
itself, it is understood as a reference to everything that was defined with that
same identifier.

Syntax
======

.. productionlist::
    Identifier: ([a-zA-Z_][a-zA-Z_0-9]*)

Examples
--------
::

    # Identifiers can begin with a lower case letter and then follow CamelCase structure
    fooBar


    # They can also start with an underscore and then follow _under_score structure
    _foo_bar_fizz_bazz_
    

    # Identifiers can also be Natural numbers
    _9
