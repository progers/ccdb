.PHONY: tests

all: examples/brokenQuicksort/brokenQuicksort tests

examples/brokenQuicksort/brokenQuicksort: examples/brokenQuicksort/brokenQuicksort.cpp
	clang++ -g -fno-inline -fprofile-instr-generate -fcoverage-mapping examples/brokenQuicksort/brokenQuicksort.cpp -o examples/brokenQuicksort/brokenQuicksort

test/data/out/inlineFunctions: test/data/inlineFunctions.cpp
	mkdir -p test/data/out
	clang++ -g -fno-inline -fprofile-instr-generate -fcoverage-mapping test/data/inlineFunctions.cpp -o test/data/out/inlineFunctions

test/data/out/filteredCoverage: test/data/filteredCoverage.cpp FilterCoverage.h
	mkdir -p test/data/out
	clang++ -g -fno-inline -fprofile-instr-generate -fcoverage-mapping test/data/filteredCoverage.cpp -o test/data/out/filteredCoverage

test/data/out/noCoverage: test/data/inlineFunctions.cpp
	mkdir -p test/data/out
	clang++ -g -fno-inline test/data/inlineFunctions.cpp -o test/data/out/noCoverage

tests: examples/brokenQuicksort/brokenQuicksort test/data/out/inlineFunctions test/data/out/filteredCoverage test/data/out/noCoverage
	python -m unittest discover

clean:
	rm -f examples/brokenQuicksort/brokenQuicksort test/data/out/inlineFunctions test/data/out/filteredCoverage test/data/out/noCoverage

