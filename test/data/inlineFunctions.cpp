// A simple program for testing inline function calls.
//
// This should be compiled with -fno-inline to ensure only annotated functions are inlined.
//
// Usage: ./inlineFunctions

#include <stdio.h>

void A();
void inlineB();
void C();
void D();

void D() {
    fprintf(stdout, "D\n");
}

void C() {
	  fprintf(stdout, "C\n");
}

__attribute__((always_inline))
inline void inlineB() {
	  fprintf(stdout, "inlineB\n");
    C();
}

void A() {
    fprintf(stdout, "A\n");
    inlineB();
}

int main(int argc, char *argv[]) {
	  fprintf(stdout, "main\n");
    A();
    return 0;
}
