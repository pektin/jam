import os
import sys
import fnmatch

TESTS_PATH = os.path.join("test", "programs")
BUILD_PATH = os.path.join("build", "tests")

class TestFile:
    def __init__(self, **entries):
        self.__dict__.update(entries)

TEST_FILES = []

for root, dirs, files in os.walk(TESTS_PATH):

    # All jam files are tests
    for file in fnmatch.filter(files, "*.jm"):
        path = os.path.join(root, file)
        name = ".".join(root.split(os.sep)[2:] + [file])

        # Make the path to the build directory
        build = os.path.join(BUILD_PATH, *os.path.normpath(path).split(os.sep)[2:])
        os.makedirs(os.path.dirname(build), exist_ok=True)
        build = os.path.splitext(build)[0]

        with open(path, "r") as program:
            assert program.read(1) == "#"

            type = program.read(1)

            expect_fail = False
            if type == "?":
                expect_fail = True
                type = program.read(1)

            if type == "#":
                has_error = False
            elif type =="!":
                has_error = True
            else:
                raise ValueError("Invalid Test Output Type for '{}': {}".format(path, type))

            output = (program.readline()[:-1].encode("UTF-8")
                                             .decode("unicode-escape")
                                             .encode("UTF-8"))

            test_file = TestFile(name = name, path = path, build = build,
                                 expect_fail = expect_fail, type = type,
                                 has_error = has_error, output = output)
            TEST_FILES.append(test_file)
