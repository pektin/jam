# Tests

This folder is a collection of all full-stack tests for jam. Each file is an
individual test with the first line indicating the expected outcome of the
program. The first line indicates the expected test result. A expected result
may start with a `?` to mark the test as expected to fail. `!<exception>` marks
the test as expected to throw an exception, `<exception>` being an exception
found in `compiler/errors.py`. `#<stdout>` details what the test is expected to
write to standard out, with `<stdout>` being a format string.

The tests are grouped into folders for specific types of tests:

* invalid_programs
    All invalid programs expected to fail
* language_features
    Programs that represent specific language features
* odds
    Tests for weird edge cases
* standard_programs
    Programs that are common and expected to work
