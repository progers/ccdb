Code Coverage Debugging
=========

Warning: This is in development and is not ready to use.

Code coverage debugging is technique where every function call is recorded for two runs of a program, then compared to see where they differ.

This technique is useful for large software projects where passing and failing testcases are available but it's not obvious where to start debugging. Many bugs in Chromium end up being trivial one-line fixes where an engineer spends hours finding a bug but only a few minutes fixing it. Code coverage debugging can be used to save time by automatically narrowing in on suspect code.

Tutorial
---------

The first step is to build the program with LLVM's code coverage by passing `-g`, `-O0`, `-fprofile-instr-generate`, and `-fcoverage-mapping` to clang++:
```
clang++ -g -O0 -fprofile-instr-generate -fcoverage-mapping program.cpp -o program
```

Then record every function call made when running the program:
```
> python record.py -o good.json ./program good_args
```

This will record a code coverage file (`good.json`) which has a format like the following:
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

The bad input didn't call `functionB(...)` but the good input did. Time to start debugging calls to `functionB(...)`.
