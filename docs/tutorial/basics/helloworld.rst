.. _tutorial-basics-helloworld:

Hello World
###########

The standard "Hello World" program is easy to write in jam. The example uses the
builtin ``puts`` function to print the string ``Hello World!`` to standard out.

::

    puts("Hello World!")

Jam source files generally have the extension ``.jm``. To compile and run a
source file, use the jam compiler script ``jam.py``.

.. code-block:: bash

    $ ./jam.py hello_world.jm

For further options, such as outputting a llvm-ir file, use the standard help
option.

.. code-block:: bash

    $ ./jam.py --help

.. note::
    The current tooling currently only exists for debugging and is not yet
    designed for popular usage. This will chance once the language and library
    become more stable.
