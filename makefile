.PHONY: tests

all: examples/brokenQuicksort/brokenQuicksort tests

examples/brokenQuicksort/brokenQuicksort: examples/brokenQuicksort/brokenQuicksort.cpp
	clang++ -g -O0 -fno-inline -fprofile-instr-generate -fcoverage-mapping examples/brokenQuicksort/brokenQuicksort.cpp -o examples/brokenQuicksort/brokenQuicksort

tests: examples/brokenQuicksort/brokenQuicksort
	python -m unittest discover

clean:
	rm examples/brokenQuicksort/brokenQuicksort
