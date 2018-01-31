import os.path
import shutil
import tempfile
import unittest

import record

class TestRecord(unittest.TestCase):

    # Ensure an error is thrown if there is no coverage data in the binary.
    def testNoCoverageError(self):
        try:
            tempOutputDir = tempfile.mkdtemp()
            rawCoverageFile = os.path.join(tempOutputDir, "coverage.profraw")
            executable = "test/data/out/noCoverage"
            self.assertRaises(AssertionError, record.recordRawCoverageFile, rawCoverageFile, executable)
        finally:
            shutil.rmtree(tempOutputDir)

if __name__ == "__main__":
    unittest.main()
