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

Tests are grouped by which language feature they test. Tests specifically for
the parser are in `syntax`. Tests for odd edge cases that should be reviewed are
in `odds`. Well known example programs are located in `standard_programs`.
