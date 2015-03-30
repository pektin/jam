#!/usr/bin/env python3

import os, sys
import argparse

from compiler.jam.compiler import compile

parser = argparse.ArgumentParser(
    prog = "jam",
    description = "The Jam Compiler",
)
parser.add_argument("input",
    help="The source file to compile",
    metavar="FILE",
    type=argparse.FileType('r'),
)
parser.add_argument("--verbose", "-v",
    help="Enable debug printing (Doesn't work yet)",
    action='count',
    required=False,
)
parser.add_argument("--output", "-o",
    help="The file to compile to",
    type=argparse.FileType('w'),
    required=False,
    default=None,
)
parser.add_argument("--run", "-r",
    help="Run the compiled file (Doesn't work yet)",
    action='store_true',
    required=False,
)
parser.add_argument("--version",
    help="Prints the version of the program",
    action='version',
    version="Jam Compiler V0.1a",
)

def main():
    args = parser.parse_args()

    if args.output is None:
        path = os.path.splitext(os.path.basename(args.input.name))[0] + ".ll"
        args.output = open(path, "w")

    compile(args.input, args.output)
    #TODO: Implement other functionality

if __name__ == "__main__":
    main()
