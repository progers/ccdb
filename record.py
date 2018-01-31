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
    # Parse each block of function counter data. The format is roughly:
    #   optional_filename.cpp:function_name:
    #     Hash: 0x456
    #     Counters: 6
    #     Function count: 3
    functionsRx = re.compile(r"^\s+(?P<fileAndFunction>.+):\n\s+Hash:\s.*\n\s+Counters:\s.*\n\s+Function\scount:\s(?P<count>.+)\n", re.MULTILINE)
    for match in functionsRx.finditer(profdata):
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
def record(executable, argsList = None, llvmToolchainPath = None, verbose = False):
    # Ensure llvm-profdata is available.
    llvmProfdata = os.path.join(llvmToolchainPath, "llvm-profdata") if llvmToolchainPath else "llvm-profdata"
    command = [ llvmProfdata, "show", "--help" ]
    proc = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = proc.communicate()
    if err != "":
        raise AssertionError(err)

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
        command = [ executable ]
        if argsList:
            command.extend(argsList)
        environment = os.environ.copy()
        environment["LLVM_PROFILE_FILE"] = rawCoverageFile
        proc = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, env=environment)
        out, err = proc.communicate()
        if err != "":
            print err
        if verbose:
            print out

        # Create the indexed coverage file.
        # See: https://llvm.org/docs/CommandGuide/llvm-profdata.html#profdata-merge
        indexedCoverageFile = os.path.join(tempOutputDir, "coverage.profdata")
        command = [ llvmProfdata, "merge", "-sparse", rawCoverageFile, "-o", indexedCoverageFile ]
        proc = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = proc.communicate()
        if err != "":
            print err
        if verbose:
            print out

        # Dump the raw counter values for each function.
        # TODO(phil): Support block or region counters instead of just function-level counters.
        # See: https://llvm.org/docs/CommandGuide/llvm-profdata.html#profdata-show
        command = [ llvmProfdata, "show", "-all-functions", "-text", rawCoverageFile ]
        proc = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
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
    parser.add_argument("-p", "--llvm-toolchain", help="Location of LLVM toolchain which should include llvm-profdata", default="")
    args, leftoverArgs = parser.parse_known_args()

    coverage = record(args.executable, argsList = leftoverArgs, llvmToolchainPath = args.llvm_toolchain, verbose = True)

    if args.demangler:
        coverage.demangle(args.demangler)
    else:
        # Try demangling using c++filt but fail silently.
        # MacOS's c++filt version is older and strips underscores by default, which is different from the latest GNU C++filt.
        # Work around this difference by forcing underscores to not be stripped using -n.
        try:
            coverage.demangle("c++filt -n")
        except:
            pass

    if args.output:
        with open (args.output, 'w') as outFile:
            outFile.write(coverage.asJson())
    else:
        print coverage.asJson()

if __name__ == "__main__":
    main()
