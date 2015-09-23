.. _tut-tooling:

Tooling
#######

Jam provides a variety of tools useful for working in the language. All of these
are accessible through the central ``jam`` binary.

Interactive
===========

Running ``jam`` without any arguments opens up an interactive compiler session.

.. code-block:: bash

    $ jam
    Jam v0.1a interactive compiler
    #|

Source can now be written directly into the terminal. Leaving a blank line will
make the tool compile and run the written source. Source written between blank
lines will currently not carry over.

Running
=======

Invoking ``jam`` on a file compiles and runs it directly. Jam source files
typically have a ``.jm`` extension.

.. code-block:: bash

    $ jam hello_world.jm
    Hello World!

Alternatively you can use the ``run`` or just ``r`` command.

.. code-block:: bash

    $ jam run hello_world.jm
    Hello World!
    $ jam r hello_world.jm
    Hello World!

Compiling
=========

Source files can also be compiled to executable binaries using the ``compile``
or just ``c`` command.

.. code-block:: bash

    $ jam compile hello_world.jm
    $ jam c hello_world.jm
    $ ./hello_world
    Hello World!

Use the ``-o`` option to specify an output file name.

.. code-block:: bash

    $ jam c hello_world.jm -o a.out
    $ ./a.out
    Hello World!

Further Options
===============

.. code-block:: bash

    $ jam r --help
    usage: jam run [-h] [-V] [-p] [-v] [source]

    positional arguments:
      source         the source file to run. Leave out for interactive mode

    optional arguments:
      -h, --help     show this help message and exit
      -V, --version  print the jam version number and terminate
      -p, --profile  run the profiler, printing profiling data after completion
      -v, --verbose  use verbose logging. Supply multiple times to increase
                     verbosity
    $ jam c --help
    usage: jam compile [-h] [-V] [-p] [-v] [-o FILE] [source]

    positional arguments:
      source                the source file to compile. Leave out to read from
                            stdin

    optional arguments:
      -h, --help            show this help message and exit
      -V, --version         print the jam version number and terminate
      -p, --profile         run the profiler, printing profiling data after
                            completion
      -v, --verbose         use verbose logging. Supply multiple times to increase
                            verbosity
      -o FILE, --output FILE
                            the file to write the executable to. Leave out to let
                            jam guess the name
