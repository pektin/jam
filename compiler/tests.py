import os
import unittest
from subprocess import check_output

from . import errors
from .jam.compiler import compile, compileRun

TESTS_PATH = os.path.join("compiler", "tests")
BUILD_PATH = os.path.join("build", "tests")

def getFiles():
    paths = os.listdir(TESTS_PATH)
    names = (os.path.splitext(path)[0] for path in paths)
    test_paths = (os.path.join(TESTS_PATH, path) for path in paths)
    build_paths = (os.path.join(BUILD_PATH, path + ".ll") for path in paths)
    return zip(names, test_paths, build_paths)

class CompilerTests(unittest.TestCase):
    pass

for file in getFiles():
    name, path, build = file
    # Ignore non-jam files
    if os.path.splitext(path)[1] != ".jm": continue

    def test(self, path=path, build=build):
        # Make the testing directories, if needed
        os.makedirs(BUILD_PATH, exist_ok=True)

        # Get output data
        with open(path, "r") as f_in, open(build, "w") as f_out:
            # The first line is the output
            first_line = f_in.readline()
            type = first_line[0]
            output = first_line[1:-1].encode("UTF-8").decode("unicode-escape")

            # Check if the output was correct
            if type == "#":
                compile(f_in, f_out)
                f_out.close()
                self.assertEqual(output, check_output(["lli-3.6", build]).decode("UTF-8"))
            # Check if the correct exception was thrown
            elif type == "!":
                with self.assertRaises(getattr(errors, output)):
                    compile(f_in, f_out)
            else:
                raise errors.InternalError("Invalid Test Output Type: {}".format(type))

    setattr(CompilerTests, "test_" + name, test)
