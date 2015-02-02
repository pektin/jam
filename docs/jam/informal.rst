.. _jam-informal:

Jam Informal Language Reference
###############################

Foreword
========

The document describes the syntax and grammar of Jam. It is designed to be ahead
of the current implementation, acting rather as a goal than documentation.
Because of the early nature of the project, this document is highly subject to
change.

Comments
========

::

    comment
    lineComment(comment):
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

    value

Identifiers
===========

::

    identifier(value):
        [_A-Za-z][_A-Za-z0-9]*
        <identifier>.<identifier>

Variable Definitions
====================

::

    variable:
        <identifier>[:<identifier>]

Assignment
==========

::

    assignment(value):
        <identifier>[, ...] [<b-op>]= <value>[, <value>[, ...]]
        <identifier>[, ...] = [<identifier>[, ...] = [...]] <value>

Method Definitions
==================

::

    method(value):
        def <identifier>[(<variable>[ = <value>][, ...])][:<return type-identifier>]
        end


Operations
==========

::

    b-op = [
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
    ]
    u-op = [
        ~
        !
    ]
    operation(value):
        <value> <b-op> <value>
        <u-op> <value>

Literals
========

::

    literal(value)
    integer(literal):
        [0-9]+
    float(literal):
        [([0-9]+\.[0-9]*)([0-9]*\.[0-9]+)]
    string(literal)
    real(string):
        `.*`
    format(string):
        ".*"
    array(literal):
        \[\]
        \[ <value>[, <value>[...]] \]
        \[ <value>[\n <value>[...]] \]
    dictionary(literal):
        \[ <value>-><value>[, <value>-><value>[...]] \]
