.. _jam-informal:

Jam Informal Language Reference
###############################

The document describes the syntax and grammar of Jam. It is designed to be ahead
of the current implementation, acting rather as a goal than documentation.
Because of the early nature of the project, this document is highly subject to
change.

Syntax
======

The syntax used to describe syntax in this document is a mix of a couple
styles, and is in no way meant to be a formal definition. A set of syntactical
elements is defined through a label (from the first indentation level). The
elements themselves use a mixture of regex, other labels (through use of
``<label>``) and braces (``[]``) used to show optional blocks. Regexes using
braces should not conflict with elements described using optional indicating
braces.

Comments
========

::

    comment:
        <lineComment>

    lineComment:
        #.*\n

Comments are pieces of text used to provide context, documentation or other
descriptions or explanations along side the rest of the code. Comments are only
compiled when debugging is enabled and are otherwise ignored.

A ``lineComment`` uses a ``#`` to mark the rest of the current time (until a
line break) as a comment.

Block comments currently do not exist and are probably unnecessary because
most editors allow for automatic commenting of multiple lines.

Values
======

::

    value:
        <identifier>
        <assignment>
        <method>
        <operation>
        <literal>

Values are the most basic syntactic item. They are the base for almost every
other piece of jam syntax. Values each have a type, which is either inferred or
specified. Some values also have a ``void`` type (``null``), which means that
they cannot be used as an input for other values, only as an instruction.

Literals
========

::

    literal:
        number
        string
        collection

    number:
        integer
        float

    integer:
        [0-9 ]+

    float:
        [0-9 ]+\.[0-9 ]*
        [0-9 ]*\.[0-9 ]+

    string:
        real
        format

    real:
        `.*`

    format:
        ".*[{<value>}.*[...]]"

    collection:
        array
        dictionary
        set

    array:
        \[\]
        \[ <value>[, <value>[...]] \]
        \[ <value>[\n <value>[...]] \]

    dictionary:
        {}
        { <value>-><value>[, <value>-><value>[...]] }
        { <value>-><value>[\n <value>-><value>[...]] }

    set:
        {}
        { <value>[, <value>[...]] }
        { <value>[\n <value>[...]] }

Literals allow direct insertion/manipulation of values_. Literals are designed
to cover the most common pieces of data.

Numbers
-------

Numbers come in two forms: Integers and Floating Points. Both literals may
contain spaces to improve readability of large numbers.

Floating point numbers may leave out either the left of right hand side of the
dot.

Strings
-------

Strings are a array of individual characters in either ascii, utf8, utf16 or
utf32 format.

Real strings simply contain the data from the source file (in the format of the
source file) from between the ````` pair.

Format strings are identical to real strings, except that their content can
contain special characters and formatting. Using a ``{}`` pair allows for
direct insertion of other values_. Inserted values_ are automatically type
casted to a string on insertion.

Special Characters:
    ``\\`` backslash
    ``\"`` double quote
    ``\a`` bell
    ``\b`` backspace
    ``\f`` formfeed
    ``\n`` linefeed (newline)
    ``\r`` carriage return
    ``\t`` horizontal tab
    ``\v`` vertical tab
    ``\xVAL..`` character with hex value ``VAL..``

Collections
-----------

Collections are values that contain other values. These values may either be
separated by commas or by newlines.

Arrays are a dynamic ordered collection of values.

Dictionaries are a mapping of one set of values to another. The mapped set of
values is unique by hash.

Sets are a unordered collection of values. The contained values are unique by
hash.

Identifiers
===========

::

    identifier:
        [_A-Za-z][_A-Za-z0-9]*
        <identifier>.<identifier>
        <identifier>;<identifier>

Identifiers are used to refer to other values_. Most values_ can be created
using an identifier, which can then later be used to refer back to the same
`value <values>`_. Since identifiers can refer to values_ that contain other
values_ with identifiers, identifiers can be strung together with
``parent.child`` syntax. Multiple identifiers may also be strung together using
a semicolon for separation.

Variables
=========

::

    variable:
        <identifier>[:<identifier>]

Variables are containers for values_. A single variable can hold one or more
values_. Variables can be used together with assignments_ and methods_. When a
variable is referenced using it's `identifier <identifiers>`_, the currently
stored `value <values>`_ is used instead of it's container. A variable's type
can either be defined, or inferred through it's usage. A variable's type may not
be changed after creation.

Assignments
===========

::

    assignment:
        <variable>[, ...] [<b-op>]= <value>[, <value>[, ...]]
        <variable>[, ...] = [<variable>[, ...] = [...]] <value>[, <value>[, ...]]

An assignment is a ``void`` `value <values>`_ that causes the right hand side
values_ to be stored in the left hand side variables_. When an assignment
includes an `operation <operations>`_, the `operation <operations>`_ performed
is consided in-place, such that the variable on the left side of the assignment
is also on the left side of the `operation <operations>`_.

A assignment that does not include an `operation <operations>`_ can assign the
same `value <values>`_ to multiple sets of variables_.

Operations
==========

::

    b-op:
        %
        ^
        &
        *
        **
        -
        +
        ==
        !=
        |
        and
        or
        is
        !is
        <
        <=
        >
        >=
        /
        //

    u-op:
        ~
        !

    operation:
        <value> <b-op> <value>
        <u-op> <value>

An operation is a shortcut to a `method <methods>`_ that operates on one to two
values_ to produce another. Operations are split between binary operations,
which act on two values, and unary operations, which only act on one.

Methods
=======

::

    method:
        def <identifier>[(<variable>[ = <value>][, ...])][:<identifier>]
            [<value>[
            ...]]
        end
