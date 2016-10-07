# Test Programs

This folder is a collection of all full-stack tests for jam. These tests are
dynamically loaded by `programs.py`.

## Test Cases

Each file represents a single test. The first line in each file is the expected
result for when the file is compiled and run. The expected result is contained
within a comment. It supports the following result formats:

* `!<error>` for a test that should fail with a specified compiler error. Use
  `CompilerError` to encompass all errors.
* `#<stdout>` for a test that should write `<stdout>` to standard out.
  `<stdout>` is a formatted string, so `/n` and other control sequences are
  supported.

Preface any expected result with a `?` to mark that test as expected to fail.

## Organisation

Tests are first grouped by what kind of test they are. Tests for error handling
are put in `invalid_programs`, tests for language features are put in
`language_features` and common programs that show off the language and act as
tests go in `standard_programs`. Tests that don't fit in these categories go in
`odds`. Tests are then grouped by what they test, if more than one test is
required to test a feature.
