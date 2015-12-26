import pytest

def pytest_addoption(parser):
    parser.addoption("--valgrind", action="store_true", default=False,
        help="Use valagrind to check for memory leaks in compiled programs")

def pytest_generate_tests(metafunc):
    # Pass the py.test -v flag to any verbosity parameters for tests
    if "verbosity" in metafunc.fixturenames:
        metafunc.parametrize("verbosity", [metafunc.config.option.verbose])
    # Do the same with --valgrind
    if "valgrind" in metafunc.fixturenames:
        metafunc.parametrize("valgrind", [metafunc.config.getoption("--valgrind")])

def pytest_collection_modifyitems(items):
    items[:] = reversed(sorted(items, key=lambda a: a.module.__name__ + a.name))
