import os, sys
import fnmatch
import logging

import pytest

from . import jam, lekvar, llvm
from . import errors

TESTS_PATH = os.path.join("compiler", "tests")
BUILD_PATH = os.path.join("build", "tests")

def compile(f_in):
    return lekvar.compile(f_in, jam, llvm)

def interpret(f_in, f_out):
    ir = compile(f_in)
    f_out.write(ir)
    return llvm.run(ir).decode("UTF-8")

for root, dirs, files in os.walk(TESTS_PATH):

    # All jam files are tests
    for file in fnmatch.filter(files, "*.jm"):
        path = os.path.join(root, file)
        name = "test_" + ".".join(root.split(os.sep)[2:] + [file])

        def test(verbosity, file=file, path=path):
            logging.basicConfig(level=logging.WARNING - verbosity*10, stream=sys.stdout)

            # Make the path to the build directory
            build = os.path.join(BUILD_PATH, *os.path.normpath(path).split(os.sep)[2:])
            os.makedirs(os.path.dirname(build), exist_ok=True)

            build = os.path.splitext(build)[0] + ".ll"

            # Get output data
            with open(path, "r") as f_in:
                # The first character is the test type
                type = f_in.read(1)
                # Or specific test attributes (ignore for now)
                if type == "?":
                    type = f_in.read(1)

                # The first line is the output
                output = f_in.readline()[:-1].encode("UTF-8").decode("unicode-escape")

                with open(build, "wb") as f_out:
                    # Check if the output was correct
                    if type == "#":
                        assert output == interpret(f_in, f_out)
                    # Check if the correct exception was thrown
                    elif type == "!":
                        with pytest.raises(getattr(errors, output)):
                            compile(f_in)
                    else:
                        raise errors.InternalError("Invalid Test Output Type: {}".format(type))

        # get test attributes
        with open(path, "r") as f:
            if f.read(1) == "?":
                test = pytest.mark.xfail(test)

        globals()[name] = test

del test
