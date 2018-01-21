Find a brokenQuicksort bug with code coverage
=========

It took years to write the advanced brokenQuicksort program. Days before shipping, a bug was discovered and assigned to you, the new person. You don't know enough about this complex code to know where to start. This tutorial will use code coverage debugging to find the bug.

Building
--------

Ensure `clang++` and `llvm-profdata` are available on the PATH. If they are not, see the first step in the main [README.md](../../README.md).
```
> which clang++
path/to/clang++

> which llvm-profdata
path/to/llvm-profdata
```

Then build the program with Clang's [source-based code coverage](https://clang.llvm.org/docs/SourceBasedCodeCoverage.html):
```
clang++ -g -fno-inline -fprofile-instr-generate -fcoverage-mapping brokenQuicksort.cpp -o brokenQuicksort
```


The bug
---------
All you know is that there's a bug with certain input:
```
> ./brokenQuicksort 1 6 3 9 0
    0 1 3 6 9 // Amazingly sorted
> ./brokenQuicksort 1 6 5 9 0
    0 1 9 6 5 // This is not sorted
```

Using code coverage debugging
--------

Begin by recording coverage for a working run of the program:
```
python ../../record.py -o working.json ./brokenQuicksort 1 6 3 9 0
```

Next, record coverage for a broken run of the program:
```
python ../../record.py -o broken.json ./brokenQuicksort 1 6 5 9 0
```

Finally, compare the two recordings:
```
python ../../compare.py working.json broken.json

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