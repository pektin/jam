import pytest

def pytest_generate_tests(metafunc):
    # Pass the py.test -v flag to any verbosity parameters for tests
    if "verbosity" in metafunc.fixturenames:
        metafunc.parametrize("verbosity", [metafunc.config.option.verbose])

def pytest_collection_modifyitems(items):
    items[:] = reversed(sorted(items, key=lambda a: a.module.__name__ + a.name))
