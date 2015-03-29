# Jam

Jam is an experimental programming language that tries to combine the advantages of dynamic, interpreted programming languages with those of static, compiled ones. Jam is based on Ruby and Python and tries to provide the same concepts that make those languages great, but supported by a powerful type system to allow the language to compile to native code. Jam compiles to an executable intermediate format called Lekvar, meaning Jam can also be interpreted in much the same way as python.

Currently the compiler is being written in python in the form of a library. The plan is to bootstrap the compiler once the language is capable and then have the compiler become part of the standard library.

## Requirements

In order to run the tests for the compiler, Jam requires Python 3 and LLVM 3.6

Ubuntu:
```bash
sudo apt-get install python3 llvm-3.6-dev
```

For documentation Jam uses Sphinx and thereby requires Python 2.X, Sphinx and make.

## Tests

Currently there is no executable compiler, however there are numerous tests that can be performed on the current implementation. The tests use the builtin unittest module for python.

To run the tests, execute the "tests" bash script by running:

```bash
./tests
```
