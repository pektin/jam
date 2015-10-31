# Jam

[![Join the chat at https://gitter.im/pektin/jam](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/pektin/jam?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

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

The compiler currently requires Python 3.4 and the llvm-3.6 shared library

### Ubuntu

See http://llvm.org/apt/ for instructions on how to set up your system to fetch
the 3.6 packages if you're still on precise.

``` bash
sudo apt-get install python3 libllvm3.6 llvm-runtime
```

### Darwin (OSX Journaled)

``` bash
brew install python3
```

Download the source for llvm 3.6 from http://llvm.org/releases/download.html
and build with:

``` bash
./configure --enable-shared --disable-assertions
make install
```

## Usage

The compiler is currently built as a python library, however it can also be
directly run through the `jam` python script. The script can be symlinked into
`/usr/local/bin` with `make install`

``` bash
jam FILE
```

For further help run:

``` bash
jam --help
```

## Development

In order to run the automated tests for the compiler, the py.test framework is
required.

``` bash
pip3 install pip3
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

To check test coverage, use `pytest-cov`.
To install:

``` bash
pip3 install pytest-cov
```

Reporting:

``` bash
# Vague Report
py.test-3 --cov=compiler
# Full html report
py.test-3 --cov=compiler --cov-report=html
```
