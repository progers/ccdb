#!/usr/bin/env python

# record.py - record code coverage.

import argparse
import json
import os.path
import shutil
import subprocess
import tempfile

from coverage.coverage import Coverage

def _parseLlvmIndexedCoverageJson(indexedCoverageJson):
    coverage = Coverage()
    decoded = json.loads(indexedCoverageJson)
    functions = decoded["data"][0]["functions"]
    for function in functions:
        coverage.addCallCount(function["name"], function["count"])
    return coverage

# Run the executable and return a Coverage object.
def record(executable, argsList, verbose):
    try:
        # Use a temporary scratch directory.
        tempOutputDir = tempfile.mkdtemp()

        # Run the executable and generate a raw coverage file.
        rawCoverageFile = os.path.join(tempOutputDir, "coverage.profraw")
        args = "" if not argsList else " " + " ".join(argsList)
        command = "LLVM_PROFILE_FILE=\"" + rawCoverageFile + "\" " + executable + args
        proc = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = proc.communicate()
        if err != "":
            print err
        if verbose:
            print out

        # Create the indexed coverage file.
        indexedCoverageFile = os.path.join(tempOutputDir, "coverage.profdata")
        command = "llvm-profdata merge -sparse " + rawCoverageFile + " -o " + indexedCoverageFile
        proc = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = proc.communicate()
        if err != "":
            print err
        if verbose:
            print out

        # Convert the indexed coverage data into JSON.
        command = "llvm-cov export " + executable + " -instr-profile=" + indexedCoverageFile
        proc = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        indexedCoverageJson, err = proc.communicate()
        if err != "":
            raise AssertionError(err)

        # Parse the indexed coverage JSON into a Coverage object.
        return _parseLlvmIndexedCoverageJson(indexedCoverageJson)
    finally:
        shutil.rmtree(tempOutputDir)

def main():
    parser = argparse.ArgumentParser(description="Record code coverage")
    parser.add_argument("executable", help="Executable to run (any additional arguments are forwarded to this executable)")
    parser.add_argument("-o", "--output", help="Output code coverage file")
    args, leftoverArgs = parser.parse_known_args()

    coverage = record(args.executable, leftoverArgs, True)
    if args.output:
        with open (args.output, 'w') as outFile:
            outFile.write(coverage.asJson())
    else:
        print coverage.asJson()

if __name__ == "__main__":
    main()
