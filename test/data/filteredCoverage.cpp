// A simple program for testing filtered code coverage output.
//
// This program makes seven function calls (A, B, C, D, E, F, and G), but only a
// subset should record code coverage (B, C, E, and F).

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

void functionE() {
    fprintf(stdout, "E\n");
}

void functionF() {
    fprintf(stdout, "F\n");
}

void functionG() {
    fprintf(stdout, "G\n");
}

int main(int argc, char *argv[]) {
    fprintf(stdout, "main\n");

    functionA();

    FilterCoverage::beginFilteringCoverage();
    functionB();
    functionC();
    FilterCoverage::endFilteringCoverage();

    functionD();

    FilterCoverage::beginFilteringCoverage();
    functionE();
    functionF();
    FilterCoverage::endFilteringCoverage();

    functionG();

    return 0;
}
