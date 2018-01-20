#!/usr/bin/env python

# compare.py - compare code coverage.

import argparse

import record
from coverage.coverage import Coverage

def _fileAndFunction(file, function):
    return (file + ": " if file else "") + function

# Return a list of human-readable function call count differences, sorted by |call count difference|.
def compare(coverageA, coverageB):
    # Map from file+function, using _fileAndFunction, to (a count, b count).
    differenceMap = {}
    for (file, function) in coverageA.functions():
        key = _fileAndFunction(file, function)
        differenceMap[key] = (coverageA.callCount(file, function), 0)
    for (file, function) in coverageB.functions():
        key = _fileAndFunction(file, function)
        aCount = differenceMap[key][0] if key in differenceMap else 0
        differenceMap[key] = (aCount, coverageB.callCount(file, function))

    # List of (|call count difference|, human readable difference).
    differences = []
    for fileAndFunction, (aCount, bCount) in differenceMap.items():
        callCountDifference = abs(aCount - bCount)
        if callCountDifference > 0:
            differenceString = fileAndFunction + " call count difference: " + str(aCount) + " != " + str(bCount)
            differences.append((callCountDifference, differenceString))

    sortedDifferences = sorted(differences, key=lambda tup: tup[0])
    return [difference[1] for difference in sortedDifferences]

def main():
    parser = argparse.ArgumentParser(description="Compare code coverage")
    parser.add_argument("coverageA", help="Coverage file for run A")
    parser.add_argument("coverageB", help="Coverage file for run B")
    args = parser.parse_args()

    with open (args.coverageA, 'r') as inFile:
        coverageA = Coverage.fromJson(inFile.read())
    with open (args.coverageB, 'r') as inFile:
        coverageB = Coverage.fromJson(inFile.read())

    differences = compare(coverageA, coverageB)
    for difference in differences:
        print difference

if __name__ == "__main__":
    main()
