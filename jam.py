#!/usr/bin/env python3

import os
import sys
import logging
import argparse
import cProfile
from io import StringIO

from compiler import jam, llvm

parser = argparse.ArgumentParser(
    prog = "jam",
    description = "The Jam Compiler",
)
parser.add_argument("input",
    help="The source file to compile.",
    metavar="FILE",
    type=argparse.FileType('r'),
    default=sys.stdin,
    nargs='?',
)
parser.add_argument("--verbose", "-v",
    help="Enable debug logging at a specific level.",
    action='count',
    default=0,
)
parser.add_argument("--output", "-o",
    help="The file to compile to.",
    type=argparse.FileType('wb'),
    default=None,
)
parser.add_argument("--compile", "-c",
    help="Instead of running, compile the input.",
    action='store_true',
)
parser.add_argument("--version",
    help="Prints the version of the program.",
    action='version',
    version="Jam Compiler V0.1a",
)
parser.add_argument("--profile",
    help="Uses cProfile to profile the compiler.",
    action='store_true',
)

def main():
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING - args.verbose*10, stream=sys.stdout)

    # Make sure we always have a compile target when we're compiling
    if args.compile and args.output is None:
        if os.path.isfile(args.input.name):
            name = os.path.splitext(os.path.basename(args.input.name))[0]
        else:
            name = "a.out"

        args.output = open(name, "wb")

    # Make the output executable if we're compiling
    if args.compile and os.path.isfile(args.output.name):
        os.chmod(args.output.name, 0o775)

    if args.profile:
        profiler = cProfile.Profile()
        profiler.enable()

    try:
        ir = parse(args.input)

        if args.compile:

            compile(ir, args.output)
        else:
            run(ir, args.output)
    finally:
        if args.profile:
            profiler.disable()
            profiler.print_stats()

def parse(input):
    return llvm.emit(jam.parse(input))

def compile(ir, output):
    output.write(llvm.compile(ir))

def run(ir, output):
    print(llvm.run(ir).decode("UTF-8"), end="")

    if output is not None:
        output.write(ir)

if __name__ == "__main__":
    main()
