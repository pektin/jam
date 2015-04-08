import pytest

def pytest_generate_tests(metafunc):
    # Pass the py.test -v fag to any verbosity parameters for tests
    if "verbosity" in metafunc.fixturenames:
        metafunc.parametrize("verbosity", [metafunc.config.option.verbose])
