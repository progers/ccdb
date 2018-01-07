#!/usr/bin/env python

# compare.py - compare code coverage.

import argparse

import record
from coverage.coverage import Coverage

def compare(coverageA, coverageB):
    differences = []
    allFunctions = coverageA.functions()
    for function in coverageB.functions():
        if function not in allFunctions:
            allFunctions.append(function)
    for (file, function) in allFunctions:
        if coverageA.callCount(file, function) != coverageB.callCount(file, function):
            differences.append(function + ": was called " + str(coverageA.callCount(file, function)) + " times, not " + str(coverageB.callCount(file, function)) + " times.")
    return differences

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
