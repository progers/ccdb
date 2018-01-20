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
        self.assertEqual(differences[0], "fn call count difference: 5 != 0")

        # Compare B vs A.
        differences = compare.compare(coverageB, coverageA)
        self.assertEqual(len(differences), 1)
        self.assertEqual(differences[0], "fn call count difference: 0 != 5")

    def testFunctionCallCountDifference(self):
        coverageA = Coverage()
        coverageA.addCallCount("", "fn", 5)
        coverageB = Coverage()
        coverageB.addCallCount("", "fn", 3)

        # Compare A vs B.
        differences = compare.compare(coverageA, coverageB)
        self.assertEqual(len(differences), 1)
        self.assertEqual(differences[0], "fn call count difference: 5 != 3")

        # Compare B vs A.
        differences = compare.compare(coverageB, coverageA)
        self.assertEqual(len(differences), 1)
        self.assertEqual(differences[0], "fn call count difference: 3 != 5")

    # Test a difference where functions with the same name are covered but the functions are different because they are in different files.
    def testDifferenceWithFiles(self):
        coverageA = Coverage()
        coverageA.addCallCount("a.cpp", "fn", 4)
        coverageB = Coverage()
        coverageB.addCallCount("b.cpp", "fn", 4)

        differences = compare.compare(coverageA, coverageB)
        self.assertEqual(len(differences), 2)
        self.assertEqual(differences[0], "b.cpp: fn call count difference: 0 != 4")
        self.assertEqual(differences[1], "a.cpp: fn call count difference: 4 != 0")

    def testDifferenceSortOrder(self):
        coverageA = Coverage()
        coverageA.addCallCount("", "a", 5)
        coverageA.addCallCount("", "b", 4)
        coverageA.addCallCount("", "c", 6)
        coverageB = Coverage()

        # Compare A vs B, call count differences should be ascending.
        differences = compare.compare(coverageA, coverageB)
        self.assertEqual(len(differences), 3)
        self.assertEqual(differences[0], "b call count difference: 4 != 0")
        self.assertEqual(differences[1], "a call count difference: 5 != 0")
        self.assertEqual(differences[2], "c call count difference: 6 != 0")

        # Compare B vs A, call count differences should be ascending.
        differences = compare.compare(coverageB, coverageA)
        self.assertEqual(len(differences), 3)
        self.assertEqual(differences[0], "b call count difference: 0 != 4")
        self.assertEqual(differences[1], "a call count difference: 0 != 5")
        self.assertEqual(differences[2], "c call count difference: 0 != 6")

    # Integration test using the broken quicksort example.
    def testBrokenQuicksortExample(self):
        executable = "examples/brokenQuicksort/brokenQuicksort"
        workingCoverage = record.record(executable, "1 6 3 9 0", False)
        brokenCoverage = record.record(executable, "1 6 5 9 0", False)

        differences = compare.compare(workingCoverage, brokenCoverage)
        self.assertEqual(len(differences), 1)
        self.assertEqual(differences[0], "_Z4swapPiii call count difference: 3 != 4")

if __name__ == "__main__":
    unittest.main()
