# The Compiler

This folder contains the current implementations of the jam lexer, the jam parser, lekvar, the lekvar verifier and the lekvar llvm emitter. It also contains a set of automated tests for each module.

The current implementation is written in python3. This is primarily due to the fact that python has a level of abstraction that is closer to Jam than C or other lower level languages. This means that bootstrapping the compiler later on will require less work. The downside to using python of course being the execution speed.
