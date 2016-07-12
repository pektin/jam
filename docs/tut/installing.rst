Installing
##########

Currently Jam is only provided as a python module. In order to install the Jam
compiler tool, clone or download the source repository from Github_. Once
downloaded, run ``make install`` to symlink all tools into your ``/usr/bin``
directory.

Jam assumes you have the following dependencies installed:

    | Python 3.4 (or later)
    | llvm-3.6 shared library (built without assertions)
    | clang-3.6

See the following sections for installing those dependencies for a specific OS/Dist.

.. note::
    Once the compiler is bootstrapped, a proper install procedure will be
    written. Until then this works well enough.

Ubuntu >= 14.04 (Trusty Tahr)
=============================

.. code-block:: shell

    apt-get install python3 libllvm3.6 llvm-runtime clang-3.6

Ubuntu < 14.04
==============

See `apt.llvm.org <http://apt.llvm.org>`_ for instructions on how to set up your
system to fetch the llvm 3.6 packages.

.. code-block:: shell

    apt-get install python3 libllvm3.6 llvm-runtime clang-3.6

Darwin (OSX Journaled)
======================

If you haven't already, install `brew <http://brew.sh>`_.

.. code-block:: shell

    brew install python3

The llvm-3.6 library on brew is built with assertions, which break the Jam code
generator. As a workaround you will have to install llvm-3.6 from source, or
make due with possible bugs.

You can download the source for llvm 3.6 from
http://llvm.org/releases/download.html and build with:

.. code-block:: shell

    ./configure --enable-shared --disable-assertions
    make install

.. _Github: https://github.com/pektin/jam
