.. _jam-builtins-constants:

Builtin Constants
#################

Numerical
=========

.. code-block:: Jam

    const inf:Real

\

    The real number representation for infinity. Use `-inf` for negative
    infinity. Infinity can be the result of the value going outside of the
    supported range, or a zero division.

.. code-block:: Jam

    const nan:Real

\

    The real number representation for not-a-number. NAN can occur for zero
    divisions like 0/0.

Boolean
=======

.. code-block:: Jam

    const true:Bool

\

    A value of `1` for the `Bool` type.

.. code-block:: Jam

    const false:Bool

\

    A value of `0` for the `Bool` type.

Objects
=======

.. code-block:: Jam

    const null

\

    A reference representing an object that is nothing.
