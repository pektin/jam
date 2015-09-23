.. _jam-visibility:

Visibility
##########

Visibility refers to certain restrictions that can be imposed on attribute
access. When the visibility of an attribute is considered "private", it can only
be accessed inside the context of it's parent, when it is considered "public" it
may be accessed from any context and when it is considered "protected", it may
only be accessed inside the context of it's parent or any inheriting context.

Visibility may only be defined in a static context, ie. one whose existence is
not dependent. The visibility is by default public.

Syntax
======

.. productionlist::
    Visibility: "public" | "private" | "protected"
