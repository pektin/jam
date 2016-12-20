# Jam

[lets Jam!](https://lets-jam.org)

[![Join the chat at https://gitter.im/pektin/jam](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/pektin/jam?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Build Status](https://travis-ci.org/pektin/jam.svg?branch=master)](https://travis-ci.org/pektin/jam)
[![Coverage Status](https://coveralls.io/repos/pektin/jam/badge.svg?branch=master&service=github)](https://coveralls.io/github/pektin/jam?branch=master)

Jam is a general purpose programming language that tries to combine the
advantages of dynamic, interpreted programming languages with those of static,
compiled ones.

See the [website](https://lets-jam.org) for more information.

Currently the compiler is being written in python, speed being a secondary
concern. The plan is to bootstrap the compiler once the language is capable.

## Dependencies

The compiler currently requires Python 3.4, the llvm-3.6 shared library and
clang-3.6

### Ubuntu (< 14.04 Trusty Tahr)

See http://llvm.org/apt/ for instructions on how to set up your system to fetch
the llvm 3.6 packages, then follow instructions for newer Ubuntu versions.

### Ubuntu (>= 14.04 Trusty Tahr)

```bash
sudo apt-get install python3 libllvm3.6 llvm-runtime clang-3.6
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

See [tutorial](https://lets-jam.org/docs/tut/tooling.html).

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

### Memory (valgrind)

To run all executables created by tests with valgrind to check for leaks and
other memory issues, pass the `--valgrind` option to `py.test`. Do note that
valgrind is slow and the tests will take a significantly longer time to run.

```bash
py.test --valgrind
```
