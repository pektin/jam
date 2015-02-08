import os
import unittest

from .jam.compiler import compileRun

TESTS_PATH = os.path.join("compiler", "tests")

def getFiles():
    paths = os.listdir(TESTS_PATH)
    names = (os.path.splitext(path)[0] for path in paths)
    paths = (os.path.join(TESTS_PATH, path) for path in paths)
    return zip(names, paths)

class CompilerTests(unittest.TestCase):
    pass

for file in getFiles():
    name, path = file
    def test(self, path=path):
        # Get output data
        with open(path, "r") as f:
            output = f.readline()[1:-1].encode("UTF-8").decode("unicode-escape")
        # compile and test
        self.assertEqual(output, compileRun(path).decode("UTF-8"))

    setattr(CompilerTests, "test_" + name, test)
