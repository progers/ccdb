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
# TODO(phil): Support block-level counters.
def _parseFunctionProfData(profdata):
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
            function = match.group("fileAndFunction")
            # If a filename is specified, remove it.
            filenameAndFunctionMatch = re.match(r"(?P<file>.+):(?P<function>.+)", function)
            if filenameAndFunctionMatch:
                function = filenameAndFunctionMatch.group("function")
            count = int(match.group("count"))
            coverage.addCallCount(function, count)
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
            raise AssertionError(err)
        if verbose:
            print out

        # Dump the raw counter values for each function.
        # TODO(phil): Support block-level counters.
        command = "llvm-profdata show -all-functions -text " + rawCoverageFile
        proc = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = proc.communicate()
        if err != "":
            raise AssertionError(err)
        return _parseFunctionProfData(out)
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
