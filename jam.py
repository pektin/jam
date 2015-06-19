#!/usr/bin/env python3

import os
import sys
import logging
import argparse
import cProfile
from io import StringIO

from compiler.errors import CompilerError
from compiler.jam import compiler

parser = argparse.ArgumentParser(
    prog = "jam",
    description = "The Jam Compiler",
)
parser.add_argument("input",
    help="The source file to compile.",
    metavar="FILE",
    type=argparse.FileType('r'),
)
parser.add_argument("--verbose", "-v",
    help="Enable debug logging at a specific level.",
    action='count',
    required=False,
    default=0,
)
parser.add_argument("--output", "-o",
    help="The file to compile to.",
    type=argparse.FileType('w'),
    required=False,
    default=None,
)
parser.add_argument("--norun", "-r",
    help="Only compile the file, don't run it. Use in conjunction with -o to compile to a target.",
    action='store_true',
    required=False,
)
parser.add_argument("--version",
    help="Prints the version of the program.",
    action='version',
    version="Jam Compiler V0.1a",
)
parser.add_argument("--profile",
    help="Uses cProfile to profile the compiler.",
    action='store_true',
    required=False,
)

def main():
    args = parser.parse_args()

    output = args.output or open(os.devnull, "w")

    compile = compiler.compile if args.norun else compiler.compileRun

    logging.basicConfig(level=logging.WARNING - args.verbose*10, stream=sys.stdout)

    if args.profile:
        profiler = cProfile.Profile()
        profiler.enable()

    with args.input, output:
        try:
            print(compile(args.input, output), end="")
        except CompilerError as e:
            message = e.args[0]
            print("{}: {}".format(type(e).__name__, message))

    if args.profile:
        profiler.disable()
        profiler.print_stats()

if __name__ == "__main__":
    main()
