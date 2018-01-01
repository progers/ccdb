from coverage.coverage import Coverage
import unittest

class TestCoverage(unittest.TestCase):

    def _simpleCoverage(self):
        coverage = Coverage()
        coverage.addCallCount("fn1", 1)
        coverage.addCallCount("fn2", 2)
        return coverage

    def testConstruction(self):
        coverage = Coverage()

    def testCallCounts(self):
        coverage = Coverage()
        coverage.addCallCount("fn1", 1)
        self.assertEquals(coverage.callCount("fn1"), 1)
        coverage.addCallCount("fn2", 2)
        self.assertEquals(coverage.callCount("fn2"), 2)
        self.assertRaises(ValueError, coverage.addCallCount, "fn1", 3)
        self.assertEquals(len(coverage.functions()), 2)

    def testJsonEncoding(self):
        coverage = self._simpleCoverage()
        self.assertEquals(coverage.asJson(), "{\"functions\": {\"fn2\": 2, \"fn1\": 1}}")

    def testJsonDecoding(self):
        coverage = self._simpleCoverage()
        self.assertEquals(Coverage.fromJson("{\"functions\": {\"fn2\": 2, \"fn1\": 1}}").asJson(), coverage.asJson())

if __name__ == "__main__":
    unittest.main()
