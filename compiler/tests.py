import os, sys
import pytest
import logging
from subprocess import check_output

from . import errors
from .jam.compiler import compile, compileRun

TESTS_PATH = os.path.join("compiler", "tests")
BUILD_PATH = os.path.join("build", "tests")

for file in os.listdir(TESTS_PATH):
    file = os.path.join(TESTS_PATH, file)

    # Ignore non-jam files
    if os.path.splitext(file)[1] != ".jm": continue

    def test(verbosity, file=file):
        logging.basicConfig(level=logging.WARNING - verbosity*10, stream=sys.stdout)

        # Get the path to the built file
        build = os.path.join(BUILD_PATH, os.path.basename(file).replace(".jm", ".ll"))

        # Make the testing directories, if needed
        os.makedirs(BUILD_PATH, exist_ok=True)

        # Get output data
        with open(file, "r") as f_in, open(build, "w") as f_out:
            # The first line is the output
            first_line = f_in.readline()
            type = first_line[0]
            output = first_line[1:-1].encode("UTF-8").decode("unicode-escape")

            # Check if the output was correct
            if type == "#":
                compile(f_in, f_out)
                f_out.close()
                assert output == check_output(["lli-3.6", build]).decode("UTF-8")
            # Check if the correct exception was thrown
            elif type == "!":
                with pytest.raises(getattr(errors, output)):
                    compile(f_in, f_out)
            else:
                raise errors.InternalError("Invalid Test Output Type: {}".format(type))

    # "add" test
    globals()["test_" + file] = test
del test
