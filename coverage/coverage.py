# coverage.py - code coverage
#
# A Coverage object has a map of functions and their call counts.
# TODO(phil): Expand this to include the segments of each function.

from collections import defaultdict
import json

class Coverage(object):

    def __init__(self):
        self._functions = defaultdict(int)

    def addCallCount(self, function, count):
        if self._functions[function]:
            raise ValueError("Function (" + function + ") call count was already recorded.")
        self._functions[function] = count

    def callCount(self, function):
        return self._functions[function]

    def functions(self):
        return self._functions.keys()

    def asJson(self, indent = None):
        encoded = {}
        encoded["functions"] = self._functions
        return json.dumps(encoded, sort_keys=False, indent=indent)

    @staticmethod
    def fromJson(string):
        coverage = Coverage()
        decoded = json.loads(string)
        functions = decoded["functions"]
        for function in functions:
            coverage.addCallCount(function, functions[function])
        return coverage
