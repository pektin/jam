Identifiers
###########

Identifiers are names used to reference values in Jam. Any identifier must
uniquely map to a single value inside the current scope, or any parent scopes.
Identifiers with a leading ``"."`` do not check the current scope for matching
values.

Identifiers may contain more than one name, separated by a ``"."``. Any names
after the first are used to access attributes on the referenced value.

Syntax
======

.. productionlist::
    Identifier: [a-zA-Z_][a-zA-Z_0-9]*
    Attribute: `Value` "." `Identifier`

Examples
========

.. note::
    These are non-working examples, purely meant to display the syntax of
    identifiers

::

    # Valid Identifiers
    fooBar
    foo_bar
    _foo_bar_
    foo9
    foo.bar
    .foo
    ._foo_._bar_

    # Invalid Identifiers
    9foo
    bar.
    foo-bar
    foo::bar
