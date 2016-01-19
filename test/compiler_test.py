import os
import sys
import fnmatch
import logging

import pytest

from compiler import jam, lekvar, llvm, errors

TESTS_PATH = os.path.join("test", "compiler")
BUILD_PATH = os.path.join("build", "tests")

def compile(f_in):
    return lekvar.compile(f_in, jam, llvm)

def interpret(f_in, f_out, precommands):
    ir = compile(f_in)
    f_out.write(ir)
    return llvm.run(ir, precommands).decode("UTF-8")

for root, dirs, files in os.walk(TESTS_PATH):

    # All jam files are tests
    for file in fnmatch.filter(files, "*.jm"):
        path = os.path.join(root, file)
        name = "test_" + ".".join(root.split(os.sep)[2:] + [file])

        def test(verbosity, valgrind, file=file, path=path):
            logging.basicConfig(level=logging.WARNING - verbosity*10, stream=sys.stdout)

            # Make the path to the build directory
            build = os.path.join(BUILD_PATH, *os.path.normpath(path).split(os.sep)[2:])
            os.makedirs(os.path.dirname(build), exist_ok=True)

            build = os.path.splitext(build)[0]

            # Get output data
            with open(path, "r") as f_in:
                # The second character is the test type
                type = f_in.read(2)[1]

                # Or specific test attributes
                if type == "?":
                    pytest.xfail()
                    type = f_in.read(1)

                # The first line is the output
                output = f_in.readline()[:-1].encode("UTF-8").decode("unicode-escape")

                # Go back to the start of the file, so error messages are formatted properly
                f_in.seek(0)

                with open(build + ".ll", "wb") as f_out:
                    # Check if the output was correct
                    if type == "#":
                        precommands = []
                        if valgrind:
                            precommands += ["valgrind", "--error-exitcode=1", "--leak-check=full",
                                            # Make valgrind output its log data to #{build}.valgrind
                                            "--log-file={}.valgrind".format(build)]
                        assert output == interpret(f_in, f_out, precommands)
                    # Check if the correct exception was thrown
                    elif type == "!":
                        with pytest.raises(getattr(errors, output)):
                            compile(f_in)
                    else:
                        raise errors.InternalError("Invalid Test Output Type: {}".format(type))

        globals()[name] = test

del test
