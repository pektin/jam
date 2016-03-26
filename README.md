# Jam

[![Join the chat at https://gitter.im/pektin/jam](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/pektin/jam?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Build Status](https://travis-ci.org/pektin/jam.svg?branch=master)](https://travis-ci.org/pektin/jam)
[![Coverage Status](https://coveralls.io/repos/pektin/jam/badge.svg?branch=master&service=github)](https://coveralls.io/github/pektin/jam?branch=master)

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

### Ubuntu (Trusty Tahr, 14.04)

See http://llvm.org/apt/ for instructions on how to set up your system to fetch
the 3.6 packages if you're still on precise.

```bash
sudo apt-get install python3 libllvm3.6 llvm-runtime
```

### Darwin (OSX Journaled)

```bash
brew install python3
```

Download the source for llvm 3.6 from http://llvm.org/releases/download.html
and build with:

```bash
./configure --enable-shared --disable-assertions
make install
```

## Usage

The Jam toolbox is entirely contained within the `jam` script. To install the
script on your local path, run `make install`.

To access the Jam REPL simply run:

```bash
jam
```

To directly execute a jam script, run:

```bash
jam FILE
```

To compile a script to an executable, run:

```bash
jam c FILE
```

For further help run:

```bash
jam --help
```

## Development

### Testing

Jam uses the [py.test framework](http://pytest.org/).

To run the tests, simply execute py.test inside the project.

```bash
py.test
```

### Debugging

Certain parts of jam make extensive use of logging. By default only `WARNING`
level logs are shown. The logging level is bound to the verbosity option. Simply
passing in a verbosity of 1 (`-v`) enables `INFO` and 2 (`-vv`) enables `DEBUG`.

```bash
py.test -vv
```

### Coverage

To check test coverage, use
[pytest-cov](https://github.com/pytest-dev/pytest-cov):

```bash
# Vague report in console
py.test --cov=compiler
# Full html report, written to htmlcov/
py.test --cov=compiler --cov-report=html
```
