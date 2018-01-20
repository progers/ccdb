import unittest

import record

class TestRecord(unittest.TestCase):

    def testProfDataParsing(self):
        coverage = record._parseNonZeroFunctionProfData("""Counters:
                  functionA:
                    Hash: 0x123
                    Counters: 1
                    Function count: 4
                  filename.cpp:functionB:
                    Hash: 0x456
                    Counters: 6
                    Function count: 3
                  main:
                    Hash: 0x000
                    Counters: 4
                    Function count: 1
                Instrumentation level: Front-end
                Functions shown: 3
                Total functions: 3
                Maximum function count: 4""")
        self.assertEquals(len(coverage.functions()), 3)
        self.assertEquals(coverage.callCount("", "functionA"), 4)
        self.assertEquals(coverage.callCount("filename.cpp", "functionB"), 3)
        self.assertEquals(coverage.callCount("", "main"), 1)

    # Integration test using the broken quicksort example.
    def testBrokenQuicksortExample(self):
        executable = "examples/brokenQuicksort/brokenQuicksort"
        coverage = record.record("", executable, "1 6 3 9 0", False)
        self.assertEqual(len(coverage.functions()), 5)
        self.assertEqual(coverage.callCount("", "_Z4swapPiii"), 3)
        self.assertEqual(coverage.callCount("", "main"), 1)
        self.assertEqual(coverage.callCount("", "_Z9quicksortPiii"), 7)
        self.assertEqual(coverage.callCount("", "_Z4sortPii"), 1)
        self.assertEqual(coverage.callCount("", "_Z9partitionPiii"), 3)

    # Test that inline functions are printed.
    def testInlines(self):
        executable = "test/data/out/inlineFunctions"
        coverage = record.record("", executable, "", False)
        # There are 5 functions in this file but 'D' is never called and should
        # be omitted.
        self.assertEqual(len(coverage.functions()), 4)
        self.assertEqual(coverage.callCount("", "main"), 1)
        self.assertEqual(coverage.callCount("", "_Z1Av"), 1)
        self.assertEqual(coverage.callCount("", "_Z7inlineBv"), 1)
        self.assertEqual(coverage.callCount("", "_Z1Cv"), 1)

    # Ensure an error is thrown if there is no coverage data in the binary.
    def testNoCoverageError(self):
        executable = "test/data/out/noCoverage"
        self.assertRaises(AssertionError, record.record, "", executable, "", False)

if __name__ == "__main__":
    unittest.main()
