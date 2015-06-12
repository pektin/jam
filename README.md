# Jam

[![Circle CI](https://circleci.com/gh/pektin/jam.svg?style=svg)](https://circleci.com/gh/pektin/jam)

Jam is an experimental programming language that tries to combine the advantages
of dynamic, interpreted programming languages with those of static, compiled
ones.

Jam is based on Ruby and Python and tries to provide the same concepts that make
those languages great, but supported by a powerful type system to allow the
language to compile to native code.

Jam compiles to an executable intermediate format called Lekvar, meaning Jam can
also be interpreted in much the same way as python.

Currently the compiler is being written in python in the form of a library. The
plan is to bootstrap the compiler once the language is capable and then have the
compiler become part of the standard library.

## Compiler

The compiler currently requires python3 and the llvm-3.4 shared library

### Ubuntu:

See http://llvm.org/apt/ for instructions on how to set up your system to fetch
the 3.4 packages.

``` bash
sudo apt-get install python3 llvm-3.4-dev llvm-runtime python3-sphinx
```

## Usage

The compiler is currently built as a python library, however it can also be
directly run through the `jam.py` script:

``` bash
./jam.py FILE
```

For further help run:

``` bash
./jam.py --help
```

## Development

In order to run the automated tests for the compiler, the py.test framework is
required.

Ubuntu:

``` bash
sudo apt-get install python3-pytest
```

To run the tests, simply execute py.test

``` bash
py.test-3
```

By default the tests are run with a logging level set at `WARNING`. The logging
level is bound to the verbosity option. Simply passing in a verbosity of 1
(`-v`) enables `INFO` and 2 (`-vv`) enables `DEBUG`.

``` bash
py.test-3 -vv
```
