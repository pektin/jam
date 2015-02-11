import os
import unittest

from .jam.compiler import compileRun

TESTS_PATH = os.path.join("compiler", "tests")
BUILD_PATH = os.path.join("build", "tests")

def getFiles():
    paths = os.listdir(TESTS_PATH)
    names = (os.path.splitext(path)[0] for path in paths)
    test_paths = (os.path.join(TESTS_PATH, path) for path in paths)
    build_paths = (os.path.join(BUILD_PATH, path) for path in paths)
    return zip(names, test_paths, build_paths)

class CompilerTests(unittest.TestCase):
    pass

for file in getFiles():
    name, path, build = file
    # Ignore non-jam files
    if os.path.splitext(path)[1] != ".jm": continue

    def test(self, path=path, build=build):
        # Get output data
        with open(path, "r") as f:
            output = f.readline()[1:-1].encode("UTF-8").decode("unicode-escape")
        # compile and test
        os.makedirs(BUILD_PATH, exist_ok=True)
        self.assertEqual(output, compileRun(path, build).decode("UTF-8"))

    setattr(CompilerTests, "test_" + name, test)
