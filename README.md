Code Coverage Debugging
=========

Warning: This is in development and is not ready to use.

Code coverage debugging is technique where every function call is recorded for two runs of a program, then compared.

This technique is useful for large software projects where passing and failing testcases are available but it's not obvious where to start debugging. Many bugs in Chromium end up being trivial one-line fixes where an engineer spends hours finding the bug but only a few minutes fixing it. Code coverage debugging can save time by methodologically narrowing in on suspect code.


Tutorial
---------

The first step is to build the program with Clang's [source-based code coverage](https://clang.llvm.org/docs/SourceBasedCodeCoverage.html) by passing `-g`, `-fprofile-instr-generate`, and `-fcoverage-mapping` to clang++:
```
clang++ -g -fprofile-instr-generate -fcoverage-mapping program.cpp -o program
```

Then record code coverage when running the program which will output a coverage file (`good.json`):
```
> python record.py -o good.json ./program good_args
```

The coverage file has a simple format where function call counts are recorded:
```
python -m json.tool good.json
{
    "main": 1,
    "functionA(...)": 1,
    "functionB(...)": 3
}
```
`main` and `functionA(...)` were called once, whereas `functionB(...)` was called 3 times.

Now record code coverage again but on a run of the program that contains a bug:
```
> python record.py -o bug.json ./program bad_args
```

Finally, compare the two runs:
```
> ./compare.py good.json bug.json

functionB(...) call count difference: 3 != 0
```

The good input called `functionB(...)` but the bad input didn't, so there is likey a bug where `functionB(...)` is not getting called.
