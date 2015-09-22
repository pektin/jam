.. _tutorial-basics-helloworld:

Hello World
###########

The standard "Hello World" program is easy to write in jam. The example uses the
builtin ``puts`` function to print the string ``Hello World!`` to standard out.

::

    puts("Hello World!")

.. seealso::

    :ref:`Builtin Functions <jam-builtin-functions>`

Jam source files generally have the extension ``.jm``. To run a source file, use
the jam compiler script ``jam``:

.. code-block:: bash

    $ ./jam hello_world.jm
    # or
    $ ./jam run hello_world.jm

You can also compile to an executable:

.. code-block:: bash

    $ ./jam c hello_world.jm
    # or
    $ ./jam compile hello_world.jm

For further options, such as verbosity and profiling run:

.. code-block:: bash

    $ ./jam --help
