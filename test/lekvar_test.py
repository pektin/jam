import sys
import logging

import pytest
from compiler import jam, lekvar, llvm, errors
from programs import TEST_FILES

for file in TEST_FILES:
    if not file.has_error:
        continue

    def test(verbosity, file = file):
        logging.basicConfig(level=logging.WARNING - verbosity*10, stream=sys.stdout)

        with open(file.path, "r") as f_in:
            error_name = file.output.decode("UTF-8")

            with pytest.raises(getattr(errors, error_name)):
                with lekvar.use(jam, llvm):
                    lekvar.compile(f_in, jam, llvm)

    if file.expect_fail:
        test = pytest.mark.xfail(test)
    globals()["test_lekvar_" + file.name] = test

del test
