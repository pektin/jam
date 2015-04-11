# The Compiler

This folder contains the current implementations of the jam lexer, the jam
parser, lekvar, the lekvar verifier and the lekvar llvm emitter. It also
contains a set of automated tests for each module.

The current implementation is written in python3. This is primarily due to the
fact that python has a level of abstraction that is closer to Jam than C or
other lower level languages. This means that bootstrapping the compiler later on
will require less work. The downside to using python of course being the
execution speed.

## Style Guide

The compiler is purposefully written in a style that is closer to the style
associated with Jam. Because of this, there are a couple specific changes from
the standard PEP8 compliant python that should be noted:

* Functions use lowerCamelCase
* Documentation is contained in comments, rather than multi-line strings and
  thereby is written before what it documents
* Generally 'declare' argument types when its not completely obvious
