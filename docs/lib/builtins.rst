.. _jam-builtins:

###############
Builtin Library
###############

The builtin library consists of a module containing a selection of constants,
functions and types that prove most useful in most circumstances. These are
always available from any scope in Jam.

.. toctree::
    :titlesonly:

    builtins/functions
    builtins/types

Constants
=========

::

    const inf:Float

\

    The real number representation for infinity. Use ``-inf`` for negative
    infinity. Infinity can be the result of the value going outside of the
    supported range, or a zero division.

::

    const nan:Float

\

    The real number representation for not-a-number. NAN can occur for zero
    divisions like ``0/0``.

::

    const true:Bool

\

    A value of ``1`` for the `Bool` type.

::

    const false:Bool

\

    A value of ``0`` for the `Bool` type.

::

    const null

\

    A reference representing an object that is nothing. Actually provided by the
    language rather than the library, ``null`` can be
    :ref:`implicitly cast<jam-type-casting>` to any
    :ref:`nullable type<jam-types-nullability>`.
