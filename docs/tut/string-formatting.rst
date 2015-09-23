.. _tut-string-formatting:

String Formatting
#################

String are denoted by a pair of ``"`` and may span multiple lines.

Interpolation
=============

.. note::

    String Interpolation is not yet supported.

In order to insert values into strings jam supports a concept called string
interpolation. Anything inside a string between a ``#{`` and a ``}`` is
cast to a ``String`` and inserted into the string.

::

    name = "Harold"

    # This will print out "My name is Harold"
    puts("My name is #{name}")

Special Characters
==================

Strings have a set of special sequences for characters not easily represented
in source code.

======== ============================
Sequence Meaning
======== ============================
``\"``   Literal ``"``
``\\``   Literal ``\``
``\0``   Null character
``\a``   BEL character
``\b``   Backspace
``\f``   Formfeed
``\n``   Newlines
``\r``   Carriage return
``\t``   Horizontal Tab
``\v``   Vertical Tab
``\#{``  Literal ``#{``
======== ============================

WYSYWYG Strings
===============

A special subset of string denoted by a pair of ````` has the same behaviour as
stings, except they do not support interpolation or special characters.

::

    # This will print `#{foo} \0 ""`
    puts(`#{foo} \0 ""`)

.. seealso::

    :ref:`Strings language reference<jam-literals-strings>`
