// A simple program for testing filtered code coverage output.
//
// This program has four function calls (A, B, C, D), but only B and C
// should record code coverage.

#include <stdio.h>
#include "../../FilterCoverage.h"

void functionA() {
    fprintf(stdout, "A\n");
}

void functionB() {
    fprintf(stdout, "B\n");
}

void functionC() {
    fprintf(stdout, "C\n");
}

void functionD() {
    fprintf(stdout, "D\n");
}

int main(int argc, char *argv[]) {
    fprintf(stdout, "main\n");

    functionA();

    FilterCoverage::beginFilteringCoverage();
    functionB();
    functionC();
    FilterCoverage::endFilteringCoverage();

    functionD();

    return 0;
}
