import os.path
import shutil
import tempfile
import unittest

from coverage.coverage import Coverage
import record

class TestCoverage(unittest.TestCase):

    def testConstruction(self):
        coverage = Coverage()

    def testCallCounts(self):
        coverage = Coverage()
        coverage.addCallCount("", "fn1", 1)
        self.assertEquals(coverage.callCount("", "fn1"), 1)
        coverage.addCallCount("", "fn2", 2)
        self.assertEquals(coverage.callCount("", "fn2"), 2)

        # "fn1" already exists in file "".
        # TODO(phil): Re-enable this test.
        # self.assertRaises(ValueError, coverage.addCallCount, "", "fn1", 3)

        # Add another "fn1" but with a different filename.
        coverage.addCallCount("file.cpp", "fn1", 3)
        self.assertEquals(coverage.callCount("file.cpp", "fn1"), 3)
        self.assertEquals(len(coverage.functions()), 3)

    def testDemangling(self):
        coverage = Coverage()
        # Demangling empty coverage should not assert.
        coverage.demangle("c++filt -n")

        # Demangling with no demangler should assert.
        self.assertRaises(AssertionError, coverage.demangle, "c--filt")

        coverage.addCallCount("", "_Z8MangledAv", 1)
        coverage.addCallCount("", "_Z8MangledBv", 3)
        coverage.addCallCount("", "NotMangledAbc", 1)
        self.assertEqual(len(coverage.functions()), 3)
        coverage.demangle("c++filt -n")
        self.assertEqual(len(coverage.functions()), 3)
        self.assertEqual(coverage.callCount("", "MangledA()"), 1)
        self.assertEqual(coverage.callCount("", "MangledB()"), 3)
        self.assertEqual(coverage.callCount("", "NotMangledAbc"), 1)

    def testJsonEncoding(self):
        coverage = Coverage()
        coverage.addCallCount("", "fn1", 1)
        coverage.addCallCount("", "fn2", 2)
        coverage.addCallCount("file.cpp", "fn3", 3)
        self.assertEquals(coverage.asJson(), "{\"files\": {\"\": {\"fn2\": 2, \"fn1\": 1}, \"file.cpp\": {\"fn3\": 3}}}")

    def testProfDataShowAllFunctionsParsing(self):
        coverage = Coverage._fromProfDataShowAllFunctions("""Counters:
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

    # Run an executable with coverage enabled, then parse the raw coverage output
    # and return a Coverage object.
    @staticmethod
    def recordCoverage(executable, argsList = None):
        try:
            # Use a temporary scratch directory for the raw coverage file.
            tempOutputDir = tempfile.mkdtemp()
            rawCoverageFile = os.path.join(tempOutputDir, "coverage.profraw")

            # Generate the raw coverage file.
            record.recordRawCoverageFile(rawCoverageFile, executable, argsList)

            # Parse the raw coverage file, returning the Coverage object.
            return Coverage.fromRawLlvmProfile(rawCoverageFile)
        finally:
            shutil.rmtree(tempOutputDir)

    # Integration test using the broken quicksort example.
    def testBrokenQuicksortExample(self):
        executable = "examples/brokenQuicksort/brokenQuicksort"
        coverage = TestCoverage.recordCoverage(executable, "1 6 3 9 0".split(" "))
        self.assertEqual(len(coverage.functions()), 5)
        self.assertEqual(coverage.callCount("", "_Z4swapPiii"), 3)
        self.assertEqual(coverage.callCount("", "main"), 1)
        self.assertEqual(coverage.callCount("", "_Z9quicksortPiii"), 7)
        self.assertEqual(coverage.callCount("", "_Z4sortPii"), 1)
        self.assertEqual(coverage.callCount("", "_Z9partitionPiii"), 3)

    # Integration test that inline functions are recorded.
    def testInlines(self):
        executable = "test/data/out/inlineFunctions"
        coverage = TestCoverage.recordCoverage(executable)
        # There are 5 functions in this file but 'D' is never called and should
        # be omitted.
        self.assertEqual(len(coverage.functions()), 4)
        self.assertEqual(coverage.callCount("", "main"), 1)
        self.assertEqual(coverage.callCount("", "_Z1Av"), 1)
        self.assertEqual(coverage.callCount("", "_Z7inlineBv"), 1)
        self.assertEqual(coverage.callCount("", "_Z1Cv"), 1)

    # Integration test using the filtered coverage executable. Only filtered
    # functions should be in the recording.
    def testFiltering(self):
        executable = "test/data/out/filteredCoverage"
        coverage = TestCoverage.recordCoverage(executable)
        # Only functions B and C should have coverage.
        self.assertEqual(coverage.callCount("", "_Z9functionAv"), 0)
        self.assertEqual(coverage.callCount("", "_Z9functionBv"), 1)
        self.assertEqual(coverage.callCount("", "_Z9functionCv"), 1)
        self.assertEqual(coverage.callCount("", "_Z9functionDv"), 0)
        self.assertEqual(coverage.callCount("", "_Z9functionEv"), 1)
        self.assertEqual(coverage.callCount("", "_Z9functionFv"), 1)
        self.assertEqual(coverage.callCount("", "_Z9functionGv"), 0)

if __name__ == "__main__":
    unittest.main()
