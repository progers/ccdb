import unittest

import record

class TestRecord(unittest.TestCase):

    def testLlvmIndexedCoverageParsing(self):
        coverage = record._parseLlvmIndexedCoverageJson("""{
                "version":"2.0.0",
                "type":"llvm.coverage.json.export",
                "data":[
                    {
                        "files":[
                            {
                                "filename":"filename.cpp",
                                "segments":[
                                    [12,39,4,1,1]
                                ],
                                "expansions":[
                                ]
                            }
                        ],
                        "functions":[
                            {
                                "name":"functionA",
                                "count":4,
                                "regions":[
                                    [12,39,16,2,4,0,0,0]
                                ],
                                "filenames":[
                                    "filename.cpp"
                                ]
                            },
                            {
                                "name":"functionB",
                                "count":3,
                                "regions":[
                                    [18,43,31,2,3,0,0,0],
                                    [28,13,28,32,3,0,0,0]
                                ],
                                "filenames":[
                                    "filename.cpp"
                                ]
                            }
                        ]
                    }
                ]
            }""")
        self.assertEquals(len(coverage.functions()), 2)
        self.assertEquals(coverage.callCount("functionA"), 4)
        self.assertEquals(coverage.callCount("functionB"), 3)

    # Integration test using the broken quicksort example.
    def testBrokenQuicksortExample(self):
        executable = "examples/brokenQuicksort/brokenQuicksort"
        workingCoverage = record.record(executable, "1 6 3 9 0", False)
        self.assertEqual(len(workingCoverage.functions()), 5)
        self.assertEqual(workingCoverage.callCount("_Z4swapPiii"), 3)
        self.assertEqual(workingCoverage.callCount("main"), 1)
        self.assertEqual(workingCoverage.callCount("_Z9quicksortPiii"), 7)
        self.assertEqual(workingCoverage.callCount("_Z4sortPii"), 1)
        self.assertEqual(workingCoverage.callCount("_Z9partitionPiii"), 3)

if __name__ == "__main__":
    unittest.main()
