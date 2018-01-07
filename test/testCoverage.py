from coverage.coverage import Coverage
import unittest

class TestCoverage(unittest.TestCase):

    def _simpleCoverage(self):
        coverage = Coverage()
        coverage.addCallCount("", "fn1", 1)
        coverage.addCallCount("", "fn2", 2)
        coverage.addCallCount("file.cpp", "fn3", 3)
        return coverage

    def testConstruction(self):
        coverage = Coverage()

    def testCallCounts(self):
        coverage = Coverage()
        coverage.addCallCount("", "fn1", 1)
        self.assertEquals(coverage.callCount("", "fn1"), 1)
        coverage.addCallCount("", "fn2", 2)
        self.assertEquals(coverage.callCount("", "fn2"), 2)
        # "fn1" already exists in file "".
        self.assertRaises(ValueError, coverage.addCallCount, "", "fn1", 3)
        # Add another "fn1" but with a different filename.
        coverage.addCallCount("file.cpp", "fn1", 3)
        self.assertEquals(coverage.callCount("file.cpp", "fn1"), 3)
        self.assertEquals(len(coverage.functions()), 3)

    def testJsonEncoding(self):
        coverage = self._simpleCoverage()
        self.assertEquals(coverage.asJson(), "{\"files\": {\"\": {\"fn2\": 2, \"fn1\": 1}, \"file.cpp\": {\"fn3\": 3}}}")

    def testJsonDecoding(self):
        coverage = self._simpleCoverage()
        self.assertEquals(Coverage.fromJson("{\"files\": {\"\": {\"fn2\": 2, \"fn1\": 1}, \"file.cpp\": {\"fn3\": 3}}}").asJson(), coverage.asJson())

if __name__ == "__main__":
    unittest.main()
