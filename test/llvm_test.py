import os
import sys
import logging
from subprocess import check_output

import pytest

from compiler import jam, lekvar, llvm, errors
from compiler.llvm import bindings as c
from programs import TEST_FILES

BUILD_PATH = "build/tests"

@pytest.yield_fixture(autouse=True)
def setup_teardown():
    os.makedirs(BUILD_PATH, exist_ok=True)
    yield

def hello_world():
    i32 = c.Int.new(32)
    module = c.Module.fromName("test")
    builder = c.Builder.new()

    puts_type = c.Function.new(i32, [c.Pointer.new(c.Int.new(8), 0)], False)
    puts = module.addFunction("puts", puts_type)
    main = module.addFunction("main", c.Function.new(i32, [], False))

    entry = main.appendBlock("entry")
    return_ = main.appendBlock("return")

    builder.positionAtEnd(entry)
    hello = builder.globalString("Hello World!", "")
    builder.call(puts, [hello], "")
    builder.br(return_)

    builder.positionAtEnd(return_)
    builder.ret(c.Value.constInt(i32, 0, False))

    module.verify()
    return module.toString()

def test_llvm_running():
    source = hello_world()

    path = os.path.join(BUILD_PATH, "llvm_running.ll")
    with open(path, 'wb') as f:
        f.write(source)

    assert b"Hello World!\n" == llvm.interpret(source)

def test_llvm_compiling():
    source = hello_world()

    path = os.path.join(BUILD_PATH, "llvm_compiling.out")
    with open(path, 'wb') as f:
        f.write(llvm.compile(source))

    os.chmod(path, 0o775)
    assert b"Hello World!\n" == check_output("./{}".format(path))

def test_module_verification_handling():
    module = c.Module.fromName("test")
    builder = c.Builder.new()

    puts = module.addFunction("puts", c.Function.new(c.Type.void(), [c.Int.new(19)], False))
    main = module.addFunction("main", c.Function.new(c.Type.void(), [], False))

    entry = main.appendBlock("")
    builder.positionAtEnd(entry)

    hello = builder.globalString("Hello World!", "")
    builder.call(puts, [hello], "")

    with pytest.raises(c.VerificationError):
        module.verify()

INVALID_SOURCE = b"""
def rec() { ret rec() }
"""

def test_lli_failure():
    with pytest.raises(errors.ExecutionError):
        llvm.interpret(INVALID_SOURCE)

def test_llc_failure():
    with pytest.raises(errors.ExecutionError):
        llvm.compile(INVALID_SOURCE)

def test_builtin_lib():
    source = llvm.emit(llvm.builtins())

    with open(BUILD_PATH + "/builtins.ll", "wb") as f:
        f.write(source)


for file in TEST_FILES:
    if file.has_error:
        continue

    def _test(verbosity, file = file):
        logging.basicConfig(level=logging.WARNING - verbosity*10, stream=sys.stdout)

        with open(file.path, "r") as f_in, open(file.build + ".ll", "wb") as f_out:
            code = lekvar.compile(f_in, jam, llvm)
            f_out.write(code)
            output = llvm.interpret(code)
            assert file.output == output

    if file.expect_fail:
        _test = pytest.mark.xfail(_test)
    globals()["test_llvm_" + file.name] = _test
