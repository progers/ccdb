Find a brokenQuicksort bug with code coverage
=========

It took years to write the advanced brokenQuicksort program. Days before shipping, a bug was discovered and assigned to you, the new person. You don't know enough about this complex code to know where to start. This tutorial will use code coverage debugging to find the bug.

## Building
Ensure `clang++` and `llvm-profdata` are available on the PATH by running the following `which` commands. If either command prints "Fail", see [Prerequisites](../../README.md#prerequisites).
```
> which clang++ && echo "Pass: clang++ was found" || echo "Fail: clang++ not found"
path/to/clang++
Pass: clang++ was found

> which llvm-profdata && echo "Pass: llvm-profdata was found" || echo "Fail: llvm-profdata not found"
path/to/llvm-profdata
Pass: llvm-profdata was found
```

Then build the program with Clang's [source-based code coverage](https://clang.llvm.org/docs/SourceBasedCodeCoverage.html):
```
cd examples/brokenQuicksort
clang++ -g -fprofile-instr-generate -fcoverage-mapping brokenQuicksort.cpp -o brokenQuicksort
```


## The bug
All you know is that there's a bug with certain input:
```
> ./brokenQuicksort 1 6 3 9 0
    0 1 3 6 9 // Amazingly sorted
> ./brokenQuicksort 1 6 5 9 0
    0 1 9 6 5 // This is not sorted
```

## Using code coverage debugging
Begin by recording coverage for a working run of the program:
```
python ../../record.py -o working.profraw ./brokenQuicksort 1 6 3 9 0
```

Next, record coverage for a broken run of the program:
```
python ../../record.py -o broken.profraw ./brokenQuicksort 1 6 5 9 0
```

Finally, compare the two recordings:
```
python ../../compare.py working.profraw broken.profraw

swap(int*, int, int) call count difference: 3 != 4
```

We have the culprit! Manual inspection or standard debugging techniques can now be used to find why `swap` is called an extra time for the broken testcase. There are only two callsites to `swap` and the second looks like a bug:
```
   33   void quicksort(int* numbers, int a, int b) {
   34       if (a < b) {
   35           int m = partition(numbers, a, b);
   36           quicksort(numbers, a, m - 1);
   37           quicksort(numbers, m + 1, b);
   38           if (numbers[a] == 5) // FIXME: What is this doing here?
-> 39               swap(numbers, a, b);
   40       }
   41   }
```

Using code coverage debugging we were able to zero in on the bug quickly and find that lines `38` and `39` should just be deleted.
