import os.path
import shutil
import tempfile
import unittest

import record

class TestRecord(unittest.TestCase):

    # Ensure an error is thrown if there is no coverage data in the binary.
    def testBinaryNotBuiltWithCoverageError(self):
        try:
            tempOutputDir = tempfile.mkdtemp()
            rawCoverageFile = os.path.join(tempOutputDir, "coverage.profraw")
            executable = "test/data/out/noCoverage"
            self.assertRaises(AssertionError, record.recordRawCoverageFile, rawCoverageFile, executable)
        finally:
            shutil.rmtree(tempOutputDir)

    # Ensure an error is thrown if the raw coverage file is not written.
    def testNoCoverageRecordedError(self):
        try:
            tempOutputDir = tempfile.mkdtemp()
            # Use an empty directory for the output file which will not write a
            # coverage file.
            rawCoverageFile = tempOutputDir
            executable = "test/data/out/inlineFunctions"
            self.assertRaises(AssertionError, record.recordRawCoverageFile, rawCoverageFile, executable)
        finally:
            shutil.rmtree(tempOutputDir)

    # Ensure a raw coverage file is written for a simple program.
    def testCoverageFileWritten(self):
        try:
            tempOutputDir = tempfile.mkdtemp()
            rawCoverageFile = os.path.join(tempOutputDir, "coverage.profraw")
            # Coverage file should not exist before recording.
            self.assertFalse(os.path.isfile(rawCoverageFile))
            executable = "test/data/out/inlineFunctions"
            record.recordRawCoverageFile(rawCoverageFile, executable)
            self.assertTrue(os.path.isfile(rawCoverageFile))
        finally:
            shutil.rmtree(tempOutputDir)

if __name__ == "__main__":
    unittest.main()
