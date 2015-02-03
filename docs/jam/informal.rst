.. _jam-informal:

Jam Informal Language Reference
###############################

Foreword
========

The document describes the syntax and grammar of Jam. It is designed to be ahead
of the current implementation, acting rather as a goal than documentation.
Because of the early nature of the project, this document is highly subject to
change.

Syntax
------

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

Identifiers
===========

::

    identifier:
        [_A-Za-z][_A-Za-z0-9]*
        <identifier>.<identifier>

Identifiers are used to refer to other objects. Most objects are created using
an identifier, which can then later be used to refer back to the same object.
Since identifiers can refer to objects that contain other objects with
identifiers, identifiers can be strung together with ``parent.child`` syntax.

Variable Definitions
====================

::

    variable:
        <identifier>[:<identifier>]

Assignment
==========

::

    assignment:
        <variable>[, ...] [<b-op>]= <value>[, <value>[, ...]]
        <variable>[, ...] = [<variable>[, ...] = [...]] <value>

Method Definitions
==================

::

    method:
        def <identifier>[(<variable>[ = <value>][, ...])][:<return type-identifier>]
            [<value>[
            ...]]
        end

Operations
==========

::

    b-op:
        %
        ^
        &
        *
        -
        +
        ==
        |
        and
        or
        <
        <=
        >=
        /
        //

    u-op:
        ~
        !

    operation:
        <value> <b-op> <value>
        <u-op> <value>

Literals
========

::

    literal:
        integer
        float
        string
        array
        dictionary

    integer:
        [0-9]+

    float:
        [([0-9]+\.[0-9]*)([0-9]*\.[0-9]+)]

    string:
        real
        format

    real:
        `.*`

    format:
        ".*"

    array:
        \[\]
        \[ <value>[, <value>[...]] \]
        \[ <value>[\n <value>[...]] \]

    dictionary:
        \[ <value>-><value>[, <value>-><value>[...]] \]
