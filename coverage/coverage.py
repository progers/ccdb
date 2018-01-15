# coverage.py - code coverage
#
# A Coverage object has a map of functions and their call counts.
# TODO(phil): Expand this to include the segments of each function.

from collections import defaultdict
import json
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

    @staticmethod
    def fromJson(string):
        coverage = Coverage()
        decoded = json.loads(string)
        files = decoded["files"]
        for file in files:
            for function in files[file]:
                coverage.addCallCount(file, function, files[file][function])
        return coverage
