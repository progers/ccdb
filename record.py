#!/usr/bin/env python

# record.py - record code coverage.

import argparse
import os.path
import re
import shutil
import subprocess
import tempfile

from coverage.coverage import Coverage

# Parse the function counter output of llvm-profdata show.
# Call counts of zero are omitted which makes the coverage data smaller.
# TODO(phil): Support block or region counters instead of just function-level counters.
def _parseNonZeroFunctionProfData(profdata):
    coverage = Coverage()
    # Strip the header ("Counters:") and footer ("Instrumentation level...").
    functionsDataMatch = re.match(r"^Counters:\n(.+)Instrumentation\slevel.*$", profdata, re.DOTALL)
    if functionsDataMatch:
        functionsData = functionsDataMatch.group(1)
        # Parse each block of function counter data. The format is roughly:
        # optional_filename.cpp:function_name:
        #   Hash: 0x456
        #   Counters: 6
        #   Function count: 3
        functionsRx = re.compile(r"^\s+(?P<fileAndFunction>.+):\n\s+Hash:\s.*\n\s+Counters:\s.*\n\s+Function\scount:\s(?P<count>.+)\n", re.MULTILINE)
        for match in functionsRx.finditer(functionsData):
            count = int(match.group("count"))
            if count == 0:
                continue
            fileAndFunction = match.group("fileAndFunction")
            fileAndFunctionMatch = re.match(r"(?P<file>.+):(?P<function>.+)", fileAndFunction)
            if fileAndFunctionMatch:
                file = fileAndFunctionMatch.group("file")
                function = fileAndFunctionMatch.group("function")
                coverage.addCallCount(file, function, count)
            else:
                coverage.addCallCount("", fileAndFunction, count)
    return coverage

# Run the executable and return a Coverage object.
def record(executable, argsList, verbose):
    # Check the executable to ensure it was built with coverage.
    with open (executable, 'r') as inFile:
        executableData = inFile.read()
    # Count the instances of __llvm_profile. A simple hello world has 34.
    if executableData.count("__llvm_profile") < 10:
        raise AssertionError("No coverage data found in executable. Ensure the \"-fprofile-instr-generate -fcoverage-mapping\" build flags are used.")

    try:
        # Use a temporary scratch directory.
        tempOutputDir = tempfile.mkdtemp()

        # Run the executable and generate a raw coverage file.
        # See: https://clang.llvm.org/docs/SourceBasedCodeCoverage.html#running-the-instrumented-program
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
        # See: https://llvm.org/docs/CommandGuide/llvm-profdata.html#profdata-merge
        indexedCoverageFile = os.path.join(tempOutputDir, "coverage.profdata")
        command = "llvm-profdata merge -sparse " + rawCoverageFile + " -o " + indexedCoverageFile
        proc = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = proc.communicate()
        if err != "":
            print err
        if verbose:
            print out

        # Dump the raw counter values for each function.
        # TODO(phil): Support block or region counters instead of just function-level counters.
        # See: https://llvm.org/docs/CommandGuide/llvm-profdata.html#profdata-show
        command = "llvm-profdata show -all-functions -text " + rawCoverageFile
        proc = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = proc.communicate()
        if err != "":
            raise AssertionError(err)
        return _parseNonZeroFunctionProfData(out)
    finally:
        shutil.rmtree(tempOutputDir)

def main():
    parser = argparse.ArgumentParser(description="Record code coverage")
    parser.add_argument("executable", help="Executable to run (any additional arguments are forwarded to this executable)")
    parser.add_argument("-o", "--output", help="Output code coverage file")
    parser.add_argument("-d", "--demangler", help="Demangler")
    args, leftoverArgs = parser.parse_known_args()

    coverage = record(args.executable, leftoverArgs, True)

    if args.demangler:
        coverage.demangle(args.demangler)

    if args.output:
        with open (args.output, 'w') as outFile:
            outFile.write(coverage.asJson())
    else:
        print coverage.asJson()

if __name__ == "__main__":
    main()
