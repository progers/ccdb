Code Coverage Debugging
=========

Warning: This is in development and is not ready to use.

Code coverage debugging is technique where every function call is recorded for two runs of a program, then compared.

This technique is useful for large software projects where passing and failing testcases are available but it's not obvious where to start debugging. Many bugs in Chromium end up being trivial one-line fixes where an engineer spends hours finding the bug but only a few minutes fixing it. Code coverage debugging can save time by methodologically narrowing in on suspect code.


## Tutorial

First, ensure `clang++` and `llvm-profdata` are available. See the [Prerequisites](#prerequisites) section, below.

Then, build the program with Clang's [source-based code coverage](https://clang.llvm.org/docs/SourceBasedCodeCoverage.html) by passing `-g`, `-fprofile-instr-generate`, and `-fcoverage-mapping` to clang++:
```
clang++ -g -fprofile-instr-generate -fcoverage-mapping program.cpp -o program
```

Then record code coverage when running the program which will output a coverage file (`good.profraw`):
```
python record.py -o good.profraw ./program good_args
```

Now record code coverage again but on a run of the program that contains a bug:
```
python record.py -o bug.profraw ./program bad_args
```

Finally, compare the two runs:
```
python compare.py good.profraw bug.profraw

functionB(...) call count difference: 3 != 0
```

The good input called `functionB(...)` but the bad input didn't, so there is likey a bug where `functionB(...)` is not getting called.

For more information, a simple walkthrough of this technique on real code is described in [examples/brokenQuicksort/README.md](examples/brokenQuicksort/README.md).


## Prerequisites

`clang++` and `llvm-profdata` need to be available on the PATH.
```
> which clang++
path/to/clang++

> which llvm-profdata
path/to/llvm-profdata
```

If these are not available on linux, release binaries can be downloaded from [llvm.org](http://releases.llvm.org/download.html) and added to the PATH with `PATH=$PATH:path/to/llvm/bin`.

If these are not available on MacOS, they can be downloaded by installing the XCode command line tools. Then run the following command to put the toolchain binaries on the PATH:
```
PATH=$PATH:`xcrun -f llvm-profdata | xargs dirname`
```
