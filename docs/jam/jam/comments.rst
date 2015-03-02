.. _jam-comments:

Comments
########

Comments allow the programmer to add a form of metadata to code in the form of
natural language. They allow a programmer to add descriptions otherwise
impossible to add with standard code for themselves or others. It is advised to
use comments in order to maintain the maintainability of code without causing
clutter.

Multiline comments do not exist, primarily because most modern code editing
tools have shortcuts to achieve the same thing.

Syntax
======

.. productionlist::
    Comment: ("#" .*
           : )

Examples
--------

::

    # Find the distance using pythag
    dist = (x**2 + y**2)**0.5

Compilation
===========

Comments are only compiled when compiling in debug mode and otherwise ignored.
