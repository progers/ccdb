import unittest

import compare
import record
from coverage.coverage import Coverage

class TestCompare(unittest.TestCase):

    def testFunctionInANotB(self):
        coverageA = Coverage()
        coverageA.addCallCount("", "fn", 5)
        coverageB = Coverage()

        # Compare A vs B.
        differences = compare.compare(coverageA, coverageB)
        self.assertEqual(len(differences), 1)
        self.assertEqual(differences[0], "fn: was called 5 times, not 0 times.")

        # Compare B vs A.
        differences = compare.compare(coverageB, coverageA)
        self.assertEqual(len(differences), 1)
        self.assertEqual(differences[0], "fn: was called 0 times, not 5 times.")

    def testFunctionCallCountDifference(self):
        coverageA = Coverage()
        coverageA.addCallCount("", "fn", 5)
        coverageB = Coverage()
        coverageB.addCallCount("", "fn", 3)

        # Compare A vs B.
        differences = compare.compare(coverageA, coverageB)
        self.assertEqual(len(differences), 1)
        self.assertEqual(differences[0], "fn: was called 5 times, not 3 times.")

        # Compare B vs A.
        differences = compare.compare(coverageB, coverageA)
        self.assertEqual(len(differences), 1)
        self.assertEqual(differences[0], "fn: was called 3 times, not 5 times.")

    # Integration test using the broken quicksort example.
    def testBrokenQuicksortExample(self):
        executable = "examples/brokenQuicksort/brokenQuicksort"
        workingCoverage = record.record(executable, "1 6 3 9 0", False)
        brokenCoverage = record.record(executable, "1 6 5 9 0", False)

        differences = compare.compare(workingCoverage, brokenCoverage)
        self.assertEqual(len(differences), 1)
        self.assertEqual(differences[0], "_Z4swapPiii: was called 3 times, not 4 times.")

if __name__ == "__main__":
    unittest.main()
