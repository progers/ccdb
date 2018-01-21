Finding a bug in Chromium (Blink) with code coverage
=========

[crbug.com/604331](https://crbug.com/604331) is a bug where one input ([bug.html](bug.html)) crashes but a slight variation of the testcase ([nobug.html](nobug.html)) does not crash. This crash occurs during painting but the culprit is likely in layout code. Unfortunately, layout is [large and complex](https://cs.chromium.org/chromium/src/third_party/WebKit/Source/core/layout/) so tracking this bug down is like finding a needle in a haystack.

This example walks through a real-world bug using code coverage debugging.

Building with coverage
--------
Special flags need to be passed to the compiler and linker to enable LLVM code coverage.
This can be done by editing the gn args:

```
gn args out/Coverage
```

Use the following args:
```
is_debug=true
is_component_build=false
use_clang_coverage=true
use_goma=true
```

Ensure gclient is up-to-date and build with coverage enabled:
```
gclient runhooks
ninja -C out/Coverage content_shell
```

Get llvm-profdata
--------
`llvm-profdata` will be used to analyze coverage, and the version needs to match the compiler.

Ensure llvm-profdata exists by running:
```
CHROMIUM_SRC=~/Desktop/chromium/src
${CHROMIUN_SRC}/src/third_party/llvm-build/Release+Asserts/bin/llvm-profdata
```

If `llvm-profdata` does not exist, it can be downloaded. As part of [crbug.com/759794](https://crbug.com/759794), `llvm-profdata` will be downloaded automatically but, for now, this is manual.
An existing tool, [`coverage.py`](https://cs.chromium.org/chromium/src/tools/code_coverage/coverage.py), downloads the correct version of `llvm-profdata` and can be abused into just downloading it. Running the following command will fail with an error but should result in `llvm-profdata` being downloaded:
```
${CHROMIUN_SRC}/tools/code_coverage/coverage.py content_shell -b out/Coverage -c out/Coverage/content_shell -o /tmp/foo
```

Narrowing in on the bug
--------

`record.py` can be used to record the call counts of all function calls. Use it to record runs for `bug.html` and `nobug.html`:
```
CHROMIUM_SRC=~/Desktop/chromium/src
python record.py --llvm-toolchain=${CHROMIUM_SRC}/third_party/llvm-build/Release+Asserts/bin/ --demangler="c++filt" ${CHROMIUM_SRC}/out/Coverage/content_shell --no-sandbox --disable-gpu --run-layout-test --single-process examples/chromiumArithmeticBug/bug.html -o bug.json
python record.py --llvm-toolchain=${CHROMIUM_SRC}/third_party/llvm-build/Release+Asserts/bin/ --demangler="c++filt" ${CHROMIUM_SRC}/out/Coverage/content_shell --no-sandbox --disable-gpu --run-layout-test --single-process examples/chromiumArithmeticBug/nobug.html -o nobug.json
```

Then use the `compare.py` script to analyze the differences.

```
> python compare.py nobug.json bug.json | grep ^blink::Layout

blink::LayoutObject::NeedsSimplifiedNormalFlowLayout() const call count difference: 30 != 29
blink::LayoutBlockFlow::MarginValues::SetNegativeMarginBefore(...) call count difference: 2 != 1
blink::LayoutBox::ScrollHeight() const call count difference: 1 != 2
...
blink::LayoutBlockFlow::AddIntrudingFloats(...) call count difference: 0 != 1
...
```

Somehow `LayoutBlockFlow::AddIntrudingFloats()` is called for `bug.html` but not `nobug.html`.

Fixing the bug
--------

Looking at [LayoutBlockFlow.cpp](https://cs.chromium.org/chromium/src/third_party/WebKit/Source/core/layout/LayoutBlockFlow.cpp), `AddIntrudingFloats` is only getting called when the bug is present.

```
void LayoutBlockFlow::RebuildFloatsFromIntruding()
{
  ...
  // Add overhanging floats from the previous LayoutBlockFlow, but only if it
  // has a float that intrudes into our space.
  if (prev) {
    LayoutBlockFlow* previous_block_flow = ToLayoutBlockFlow(prev);
    logicalTopOffset -= previous_block_flow->LogicalTop();
    if (previous_block_flow->LowestFloatLogicalBottom() > logicalTopOffset)
      AddIntrudingFloats(previous_block_flow, LayoutUnit(), logicalTopOffset);
  ...
```

Chromium uses fixed-point units (`LayoutUnit`) with [saturated arithmetic](https://en.wikipedia.org/wiki/Saturation_arithmetic) (i.e., max + 100 = max). The bug is that two huge values are being compared and their difference is incorrect due to saturated arithmetic. Here's a simpler example which demonstrates the bug:
```
   LayoutUnit a = (LayoutUnit::max() + 1000);
   LayoutUnit b = (LayoutUnit::max() + 10);
   if (a > b)
        // This is hit if normal arithmetic is used.
   else
        // This is hit when saturated arithmetic is used because a == b!
```

The fix for this bug landed in [6c961fe1112914b9d63d6551e31b96c415dfb83f](https://crrev.com/6c961fe1112914b9d63d6551e31b96c415dfb83f) and simply re-ordered the operations to avoid a saturated arithmetic bug.

Wrapup
--------
This is a real example where locating the root-cause of a bug is time consuming: it took roughly 12 hours for an experienced engineer. Looking through the output of `compare.py` can take a little while but is a straightforward task. For this bug, code coverage debugging would have saved over a day of debugging!