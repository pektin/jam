import sys
import logging

import pytest
from compiler import jam, lekvar, interpreter, errors
from programs import TEST_FILES

for file in TEST_FILES:
    if file.has_error:
        continue

    def test(verbosity, file = file):
        logging.basicConfig(level=logging.WARNING - verbosity*10, stream=sys.stdout)

        with open(file.path, "r") as f_in:
            output = lekvar.run(f_in, jam, interpreter)
            assert file.output == output

    if file.expect_fail:
        test = pytest.mark.xfail(test)
    globals()["test_interpreter_" + file.name] = test

del test
