# coverage.py - code coverage
#
# A Coverage object has a map of functions and their call counts. This class
# also has supporting functions for parsing raw LLVM code coverage profiles.

from collections import defaultdict
import json
import re
import subprocess

class Coverage(object):

    def __init__(self):
        # Map from (file, function) to call count.
        self._callcounts = defaultdict(int)

    def addCallCount(self, file, function, count):
        # TODO(phil): Re-enable this check.
        #if self._callcounts[(file, function)]:
        #    raise ValueError("Function " + function + " in " + file + " call count was already recorded.")
        self._callcounts[(file, function)] = count

    def callCount(self, file, function):
        return self._callcounts[(file, function)]

    # Return a list of all (file, function) pairs.
    def functions(self):
        return self._callcounts.keys()

    # Use a demangler to convert mangled function names to demangled function names.
    # See c++filt: https://linux.die.net/man/1/c++filt
    # For example: _Z1Av => A().
    def demangle(self, demangler):
        mangledCallCounts = self._callcounts
        mangledFunctions = []
        for (file, function) in mangledCallCounts:
            mangledFunctions.append(function)

        proc = subprocess.Popen(demangler, shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = proc.communicate("\n".join(mangledFunctions))
        if err != "":
            raise AssertionError(err)
        demangledFunctions = filter(None, out.split("\n"))

        mangledFunctionCount = len(mangledFunctions)
        demangledFunctionCount = len(demangledFunctions)
        if mangledFunctionCount != demangledFunctionCount:
            raise AssertionError("Demangling failed: tried to demangle " + str(mangledFunctionCount) + " functions but " + str(demangledFunctionCount) + " were demangled.")

        demangledFunctionMap = {}
        for index, mangledFunction in enumerate(mangledFunctions):
            demangledFunctionMap[mangledFunction] = demangledFunctions[index]

        # Reset _callcounts then rebuild it from the demangled mapping.
        self._callcounts = defaultdict(int)
        for (file, mangledFunction), count in mangledCallCounts.items():
            demangledFunction = demangledFunctionMap[mangledFunction]
            self.addCallCount(file, demangledFunction, count)

    def asJson(self, indent = None):
        encoded = {}
        encoded["files"] = {}
        for (file, function) in self._callcounts:
            if not file in encoded["files"]:
                encoded["files"][file] = {}
            encoded["files"][file][function] = self._callcounts[(file, function)]
        return json.dumps(encoded, sort_keys=False, indent=indent)

    # Parse the function counter output of llvm-profdata show and return a
    # Coverage object.
    @staticmethod
    def _fromProfDataShowAllFunctions(profdata):
        coverage = Coverage()
        # The format is roughly:
        #   optional_filename.cpp:function_name:
        #     Hash: 0x456
        #     Counters: 6
        #     Function count: 3
        # TODO(phil): Support block or region counters instead of just function-level counters.
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

    # Convert a raw LLVM profile coverage file into a Coverage object.
    @staticmethod
    def fromRawLlvmProfile(rawProfDataPath, llvmToolchainPath = None):
        # Ensure llvm-profdata is available.
        llvmProfdata = "llvm-profdata"
        command = [ llvmProfdata, "show", "--help" ]
        proc = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = proc.communicate()
        if err != "":
            raise AssertionError(err)

        # Use llvm-profdata to dump the raw counter values for each function.
        # See: https://llvm.org/docs/CommandGuide/llvm-profdata.html#profdata-show
        # TODO(phil): Support block or region counters instead of just function-level counters.
        command = [ llvmProfdata, "show", "-all-functions", "-text", rawProfDataPath ]
        proc = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = proc.communicate()
        if err != "":
            raise AssertionError(err)

        return Coverage._fromProfDataShowAllFunctions(out)
