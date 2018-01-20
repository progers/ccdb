#!/usr/bin/env python

# compare.py - compare code coverage.

import argparse

import record
from coverage.coverage import Coverage

def compare(coverageA, coverageB):
    differences = []

    # Map from file+function to {file, function, aCallCount, bCallCount}.
    allFunctionsMap = {}
    for (file, function) in coverageA.functions():
        key = file + function
        allFunctionsMap[key] = {}
        allFunctionsMap[key]["file"] = file
        allFunctionsMap[key]["function"] = function
        allFunctionsMap[key]["aCallCount"] = coverageA.callCount(file, function)
        allFunctionsMap[key]["bCallCount"] = 0
    for (file, function) in coverageB.functions():
        key = file + function
        if key not in allFunctionsMap:
            allFunctionsMap[key] = {}
            allFunctionsMap[key]["file"] = file
            allFunctionsMap[key]["function"] = function
            allFunctionsMap[key]["aCallCount"] = 0
        allFunctionsMap[key]["bCallCount"] = coverageB.callCount(file, function)

    for key in allFunctionsMap:
        aCallCount = allFunctionsMap[key]["aCallCount"]
        bCallCount = allFunctionsMap[key]["bCallCount"]
        if aCallCount != bCallCount:
            file = allFunctionsMap[key]["file"]
            function = allFunctionsMap[key]["function"]
            fileAndFunction = (file + ": " if file else "") + function
            differences.append(fileAndFunction + " call count difference: " + str(aCallCount) + " != " + str(bCallCount))
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
