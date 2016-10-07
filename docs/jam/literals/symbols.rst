Symbols
#######

A symbol is very similar to a string, except that they follow the same rules as
identifiers and are unique. All symbols are part of a global symbols table and
thereby identical symbols are identical objects.

Syntax
======

.. productionlist::
    Symbol: "$" `Identifier`

Examples
--------
::

    foo = $symbol
    bar = "symbol"
    baz = $symbol

    # foo and baz hold the same object
    puts(foo is baz) #=> true

    # foo, baz and bar all hold the same data
    puts(foo == bar == baz) #=> true

    # foo (or baz) does not hold the same object as bar
    puts(foo is bar) #=> false
