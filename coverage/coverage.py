# coverage.py - code coverage
#
# A Coverage object has a map of functions and their call counts.
# TODO(phil): Expand this to include the segments of each function.

from collections import defaultdict
import json

class Coverage(object):

    def __init__(self):
        # Map from (file, function) to call count.
        self._callcounts = defaultdict(int)

    def addCallCount(self, file, function, count):
        if self._callcounts[(file, function)]:
            raise ValueError("Function " + function + " in " + file + " call count was already recorded.")
        self._callcounts[(file, function)] = count

    def callCount(self, file, function):
        return self._callcounts[(file, function)]

    # Return a list of all (file, function) pairs.
    def functions(self):
        return self._callcounts.keys()

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
