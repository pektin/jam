Null
####

The ``null`` value represents nothing.

.. note::

    The ``null`` value can only be assigned to
    :doc:`nullable types<../../lib/builtins/types>`.

Syntax
======

.. productionlist::
    Null: "null"

Examples
--------
::

    # null can only be assigned to nullable variables
    woman:Person? = null


    # nullable types can only be operated on inside a null check
    if woman !is null
      puts(woman.surname)
    end


