
Jam Informal Language Reference
###############################

Foreword
========

The document describes the syntax and grammar of Jam. It is designed to be ahead
of the current implementation, acting rather as a goal than documentation.
Because of the early nature of the project, this document is subject to change.

Identifiers
===========

::

    <identifier>

Like in many languages, identifiers can start with any alpha character including
an underscore and can contain any alpha-numeric characters including an
underscore. This equates to the following regex: ``[_A-Za-z][_A-Za-z0-9]*``

Variable Definitions
====================

::
    <variable>
        <variable-identifier>[:<type-identifier>]

Variable definitions contain a mandatory identifier, with an optional type
declaration.

Method Definitions
==================

::

    <method>
        def <method-identifier>(<argument-variable> = <default-value>, ...)[:<return type-identifier>]
