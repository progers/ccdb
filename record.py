#!/usr/bin/env python

# record.py - Helper for running a program and recording a raw coverage file.
#
# Usage: record.py executable -o coverage.profraw
#
# This is just a convenience tool for running an executable that has coverage
# enabled using the LLVM_PROFILE_FILE environmental variable. For information
# about doing this manually, see:
# https://clang.llvm.org/docs/SourceBasedCodeCoverage.html#running-the-instrumented-program

import argparse
import os.path
import subprocess

# Run the executable and generate a raw coverage file (*.profraw).
def recordRawCoverageFile(outputFile, executable, argsList = None, verbose = False):
    # Check the executable to ensure it was built with coverage.
    with open (executable, 'r') as inFile:
        executableData = inFile.read()
    # Count the instances of __llvm_profile. A simple hello world has 34.
    if executableData.count("__llvm_profile") < 10:
        raise AssertionError("No coverage data found in executable. Ensure the \"-fprofile-instr-generate -fcoverage-mapping\" build flags are used.")

    # If the output file already exists, delete it before writing a new one.
    if os.path.isfile(outputFile):
        os.remove(outputFile)

    # Run the executable and generate a raw coverage file.
    # See: https://clang.llvm.org/docs/SourceBasedCodeCoverage.html#running-the-instrumented-program
    command = [ executable ]
    if argsList:
        command.extend(argsList)
    environment = os.environ.copy()
    environment["LLVM_PROFILE_FILE"] = outputFile
    proc = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, env=environment)
    out, err = proc.communicate()
    if verbose:
        if err != "":
            print err
        print out

    # Ensure the raw code coverage file was written.
    if not os.path.isfile(outputFile):
        raise AssertionError("Raw code coverage was not saved to \"" + outputFile + "\"" + (": " + err if err else ""))

def main():
    parser = argparse.ArgumentParser(description="Record code coverage")
    parser.add_argument("executable", help="Executable to run (any additional arguments are forwarded to this executable)")
    parser.add_argument("-o", "--output", help="Output raw code coverage file")
    args, leftoverArgs = parser.parse_known_args()

    recordRawCoverageFile(args.output, args.executable, argsList = leftoverArgs, verbose = True)

if __name__ == "__main__":
    main()
