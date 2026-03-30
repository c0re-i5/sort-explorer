#!/usr/bin/env python3
"""
04_beyond_comparison.py — Breaking the n log n Barrier

Script 02 proved that comparison-based sorting can't beat O(n log n). But
what if we don't compare elements at all? What if we use the VALUES of the
elements to determine their position directly?

That's the trick behind counting sort, radix sort, and bucket sort. They
break the barrier by exploiting structure in the data — specifically, the
fact that elements are bounded integers or uniformly distributed numbers.

The catch: these algorithms have constraints that comparison sorts don't.
They need to know the range of values, or the distribution, or the number
of digits. The O(n) in their complexity hides factors that depend on these
constraints. There's no free lunch — but the lunch can be very cheap if
the conditions are right.

Topics: the decision tree proof (revisited) · counting sort · stable counting sort
· radix sort (LSD and MSD) · digit decomposition and number bases [← repo 7] ·
bucket sort · the tradeoff between time and assumptions
"""

import random
import time
import math

# ─────────────────────────────────────────────────────────────────────────────
#  UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def section(title):
    w = 72
    print()
    print("═" * w)
    print(f"  {title}")
    print("═" * w)
    print()


def subsection(title):
    print()
    print(f"  ── {title} ──")
    print()


# ─────────────────────────────────────────────────────────────────────────────
#  WHY THE BARRIER EXISTS (AND WHY IT DOESN'T ALWAYS APPLY)
# ─────────────────────────────────────────────────────────────────────────────

section("WHY THE n log n BARRIER EXISTS — AND HOW TO DODGE IT")

print("""\
  The comparison lower bound proof (Script 02) says:

    Any algorithm that sorts by comparing elements must examine at least
    ⌈log₂(n!)⌉ ≈ n log₂ n pairs in the worst case.

  But this applies ONLY to comparison-based sorting. The proof assumes the
  algorithm can only learn about the data through pairwise comparisons.

  What if we can do more? What if we can:
    • Use an element's value as an array index → COUNTING SORT
    • Decompose values into digits and sort digit-by-digit → RADIX SORT
    • Distribute elements into buckets by value range → BUCKET SORT

  These algorithms don't compare elements. They bypass the decision tree
  entirely. They can sort in O(n) — but with strings attached.

  ┌────────────────────┬──────────────────────────────────────────────┐
  │ Comparison sorts   │ No assumptions about data, but ≥ O(n log n) │
  │ Non-comparison     │ Assumptions about data, but can reach O(n)  │
  └────────────────────┴──────────────────────────────────────────────┘
""")


# ─────────────────────────────────────────────────────────────────────────────
#  COUNTING SORT — Mailbox Sorting
# ─────────────────────────────────────────────────────────────────────────────

section("COUNTING SORT — Mailbox Sorting")

print("""\
  Imagine a mail room with mailboxes numbered 0 through k. Each letter has
  a number on it. To sort: drop each letter in the matching mailbox, then
  collect from box 0, then 1, then 2, ... Done. No comparisons.

  That's counting sort. It works when elements are integers in a known
  range [0, k].

  Step 1: Count how many times each value appears.
  Step 2: Compute prefix sums (cumulative counts) to determine positions.
  Step 3: Place each element at its computed position.

  Time: O(n + k) where k is the range of values.
  Space: O(n + k) for the count array and output array.

  When k ≤ n (range is small), this is O(n). Truly linear.
  When k >> n (huge range), this is worse than comparison sort — the count
  array alone eats O(k) memory. That's the catch.
""")

print("  The Algorithm:")
print("  ─────────────")
print("""\
  def counting_sort(arr, max_val):
      count = [0] * (max_val + 1)
      for x in arr:
          count[x] += 1

      output = []
      for val in range(max_val + 1):
          output.extend([val] * count[val])
      return output
""")


def counting_sort_simple(arr, max_val=None):
    """Simple counting sort: O(n + k)."""
    if not arr:
        return []
    if max_val is None:
        max_val = max(arr)
    count = [0] * (max_val + 1)
    for x in arr:
        count[x] += 1
    output = []
    for val in range(max_val + 1):
        output.extend([val] * count[val])
    return output


demo = [4, 2, 2, 8, 3, 3, 1, 7, 5, 4, 6, 1, 3]
print(f"  Input: {demo}")
print()

# Show the counting process
max_val = max(demo)
count = [0] * (max_val + 1)
for x in demo:
    count[x] += 1

print("  Step 1 — Count occurrences:")
for val in range(max_val + 1):
    bar = "█" * count[val] + " " * (5 - count[val])
    if count[val] > 0:
        print(f"    Value {val}: {bar} ({count[val]})")

print()
print("  Step 2 — Collect from mailboxes in order:")
result = counting_sort_simple(demo)
print(f"    {result}")
print()


subsection("Stable Counting Sort — Order Preserved")

print("""\
  The simple version above doesn't preserve relative order of equal elements.
  For a STABLE counting sort (needed by radix sort), we use prefix sums:

  1. Count occurrences.
  2. Compute prefix sums: count[i] = count[i-1] + count[i]
     Now count[v] tells us where the LAST element with value v goes.
  3. Walk the input array BACKWARD, placing each element at count[v] - 1,
     then decrement count[v].

  Walking backward + decrementing ensures equal elements keep their order.
""")


def counting_sort_stable(arr, max_val=None, key=None):
    """Stable counting sort using prefix sums."""
    if not arr:
        return []
    if key is None:
        key = lambda x: x
    if max_val is None:
        max_val = max(key(x) for x in arr)

    count = [0] * (max_val + 1)
    for x in arr:
        count[key(x)] += 1

    # Prefix sum
    for i in range(1, len(count)):
        count[i] += count[i - 1]

    output = [None] * len(arr)
    # Walk backward for stability
    for x in reversed(arr):
        count[key(x)] -= 1
        output[count[key(x)]] = x

    return output


# Demonstrate stability
students = [(85, "Alice"), (92, "Bob"), (85, "Carol"), (78, "Dave"), (92, "Eve")]
print(f"  Students (grade, name): {students}")
sorted_students = counting_sort_stable(students, max_val=100, key=lambda s: s[0])
print(f"  Stable sort by grade:   {sorted_students}")
print(f"  Alice before Carol (both 85)? {'Yes' if sorted_students.index((85, 'Alice')) < sorted_students.index((85, 'Carol')) else 'No'} ← stability preserved")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  RADIX SORT — Digit by Digit
# ─────────────────────────────────────────────────────────────────────────────

section("RADIX SORT — Digit by Digit")

print("""\
  What if values have a large range but a small number of digits? Sort by
  the least significant digit first, then the next, then the next — using
  a STABLE sort for each digit pass.

  This is radix sort. It processes d digits, each pass using counting sort
  on a single digit position (base b). Total: O(d × (n + b)).

  For 32-bit integers with base 256 (byte-at-a-time): d=4, b=256.
  Total: O(4 × (n + 256)) = O(n). Linear in practice.

  Two flavors:
    LSD (Least Significant Digit first): sort by ones, then tens, then
        hundreds. Simple, stable, parallel-friendly.
    MSD (Most Significant Digit first): sort by highest digit, then
        recursively sub-sort each bucket. Like sorting words alphabetically.
""")


subsection("LSD Radix Sort — From Right to Left")

print("""\
  Example: Sort [329, 457, 657, 839, 436, 720, 355]

  Pass 1 (ones digit):
    Buckets: 0:[720] 5:[355] 6:[436] 7:[457,657] 9:[329,839]
    Collect: [720, 355, 436, 457, 657, 329, 839]

  Pass 2 (tens digit):
    Buckets: 2:[720,329] 3:[436,839] 5:[355,457,657]
    Collect: [720, 329, 436, 839, 355, 457, 657]

  Pass 3 (hundreds digit):
    Buckets: 3:[329,355] 4:[436,457] 6:[657] 7:[720] 8:[839]
    Collect: [329, 355, 436, 457, 657, 720, 839]  ✓ Sorted!

  Each pass is O(n + 10) with counting sort. Three passes → O(3(n + 10)).
  With n = 7 and at most 3 digits: total work ≈ 51 (compare to n²=49).
  With n = 1,000,000: total work ≈ 3,000,030 (vs. n log n ≈ 20,000,000).
""")


def lsd_radix_sort(arr, base=10):
    """LSD radix sort: sort by each digit from least to most significant."""
    if not arr:
        return []
    arr = arr[:]
    max_val = max(arr)
    exp = 1
    passes = 0

    while max_val // exp > 0:
        # Counting sort on digit at position exp
        count = [0] * base
        for x in arr:
            digit = (x // exp) % base
            count[digit] += 1

        # Prefix sum
        for i in range(1, base):
            count[i] += count[i - 1]

        output = [0] * len(arr)
        for x in reversed(arr):
            digit = (x // exp) % base
            count[digit] -= 1
            output[count[digit]] = x

        arr = output
        exp *= base
        passes += 1

    return arr, passes


demo = [329, 457, 657, 839, 436, 720, 355]
print(f"  Input: {demo}")
result, passes = lsd_radix_sort(demo)
print(f"  Sorted: {result}  ({passes} passes)")
print()


subsection("Radix Sort in Different Bases [← Repo 7: Number Systems]")

print("""\
  The base (radix) is a tunable parameter. Higher base = fewer passes
  but larger counting arrays (more memory).

  Base 10:   d = ⌈log₁₀(max)⌉ passes,  counting array = 10 slots
  Base 256:  d = ⌈log₂₅₆(max)⌉ passes, counting array = 256 slots
  Base 2:    d = ⌈log₂(max)⌉ passes,   counting array = 2 slots (slow!)

  This connects directly to number systems from repo 7: every number has
  a representation in every base. Radix sort exploits positional notation —
  the same insight that makes binary, hex, and decimal work.

  And it connects to bit tricks from repo 1: extracting digit k in base 2^b
  from integer x is just (x >> (k * b)) & ((1 << b) - 1) — a shift and mask.
""")

n = 100000
data = random.sample(range(n * 100), n)

print(f"  n = {n:,},  max value ≈ {n * 100:,}")
print()
print(f"  {'Base':>6s}  {'Passes':>8s}  {'Time':>10s}  {'Count array size':>18s}")
print(f"  {'─'*6}  {'─'*8}  {'─'*10}  {'─'*18}")

for base in [2, 10, 16, 256, 65536]:
    t0 = time.perf_counter()
    _, passes = lsd_radix_sort(data, base=base)
    elapsed = time.perf_counter() - t0
    print(f"  {base:>6d}  {passes:>8d}  {elapsed:>9.4f}s  {base:>18,} slots")

print()
print("  Sweet spot: base 256 (one byte at a time). Few passes, manageable memory.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  MSD RADIX SORT — Top-Down Variant
# ─────────────────────────────────────────────────────────────────────────────

subsection("MSD Radix Sort — From Left to Right")

print("""\
  MSD radix sort processes the most significant digit first, then recursively
  sorts within each bucket. It's how you'd sort words alphabetically:
  first letter, then within each first-letter group, second letter, etc.

  Advantage: can stop early for variable-length keys (strings).
  Disadvantage: more complex (recursion), less cache-friendly than LSD.

  MSD radix sort is the basis of BURSTSORT and other fast string sorts.
""")


def msd_radix_sort(arr, base=10, exp=None, max_val=None):
    """MSD radix sort: recursive, most significant digit first."""
    if len(arr) <= 1:
        return arr
    if max_val is None:
        max_val = max(arr) if arr else 0
    if exp is None:
        exp = 1
        while exp * base <= max_val:
            exp *= base

    if exp < 1:
        return arr

    buckets = [[] for _ in range(base)]
    for x in arr:
        digit = (x // exp) % base
        buckets[digit].append(x)

    result = []
    for bucket in buckets:
        if len(bucket) > 1 and exp >= base:
            result.extend(msd_radix_sort(bucket, base, exp // base, max_val))
        else:
            result.extend(bucket)

    return result


demo = [329, 457, 657, 839, 436, 720, 355]
print(f"  Input: {demo}")
result = msd_radix_sort(demo)
print(f"  Sorted: {result}")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  BUCKET SORT — Divide by Distribution
# ─────────────────────────────────────────────────────────────────────────────

section("BUCKET SORT — Divide by Distribution")

print("""\
  If elements are uniformly distributed on [0, 1), scatter them into n
  equally-spaced buckets. Each bucket gets ~1 element on average. Sort
  each bucket (with insertion sort), then concatenate.

  Expected time: O(n + n + k) ≈ O(n) when distribution is uniform.
  Worst case: O(n²) if all elements land in one bucket (degenerate).

  Bucket sort is the algorithm behind:
    • Hash-based grouping in databases
    • Histogram equalization in image processing
    • Distributing work in parallel systems

  It assumes knowledge of the data distribution. If you know elements are
  uniformly distributed (e.g., random floats), bucket sort is nearly optimal.
""")


def bucket_sort(arr, num_buckets=None):
    """Bucket sort for floats in [0, 1)."""
    n = len(arr)
    if n <= 1:
        return arr[:]
    if num_buckets is None:
        num_buckets = n

    buckets = [[] for _ in range(num_buckets)]
    for x in arr:
        idx = min(int(x * num_buckets), num_buckets - 1)
        buckets[idx].append(x)

    # Sort each bucket with insertion sort
    for bucket in buckets:
        for i in range(1, len(bucket)):
            key = bucket[i]
            j = i - 1
            while j >= 0 and bucket[j] > key:
                bucket[j + 1] = bucket[j]
                j -= 1
            bucket[j + 1] = key

    result = []
    for bucket in buckets:
        result.extend(bucket)
    return result


# Demonstrate
random.seed(42)
demo = [random.random() for _ in range(12)]
print(f"  Input (12 random floats in [0,1)):")
for i in range(0, 12, 4):
    print(f"    {demo[i]:.4f}  {demo[i+1]:.4f}  {demo[i+2]:.4f}  {demo[i+3]:.4f}")

result = bucket_sort(demo)
print(f"\n  Sorted:")
for i in range(0, 12, 4):
    print(f"    {result[i]:.4f}  {result[i+1]:.4f}  {result[i+2]:.4f}  {result[i+3]:.4f}")
print()


subsection("Bucket Sort vs. Comparison Sort on Uniform Data")

print(f"  Uniform floats in [0, 1):")
print()
print(f"  {'n':>8s}  {'Bucket Sort':>12s}  {'Python sort':>12s}  {'Ratio':>8s}")
print(f"  {'─'*8}  {'─'*12}  {'─'*12}  {'─'*8}")

for n in [10000, 50000, 100000, 500000]:
    data = [random.random() for _ in range(n)]

    t0 = time.perf_counter()
    bucket_sort(data)
    t_bucket = time.perf_counter() - t0

    d2 = data[:]
    t0 = time.perf_counter()
    d2.sort()
    t_py = time.perf_counter() - t0

    ratio = t_bucket / t_py if t_py > 0 else float('inf')
    print(f"  {n:>8d}  {t_bucket:>11.4f}s  {t_py:>11.4f}s  {ratio:>7.1f}×")

print()
print("  On uniform data, bucket sort is competitive. Python's Timsort still wins")
print("  due to C optimization, but the algorithmic complexity is O(n) vs O(n log n).")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  RADIX SORT vs. COMPARISON SORT: THE GRAND RACE
# ─────────────────────────────────────────────────────────────────────────────

section("THE GRAND RACE — Radix vs. Comparison Sorts")

print("""\
  Let's time everything head-to-head on integer data.
""")

def quicksort_bench(arr):
    arr = arr[:]
    def _qs(a, lo, hi):
        if lo < hi:
            pivot = a[(lo + hi) // 2]
            i, j = lo, hi
            while i <= j:
                while a[i] < pivot: i += 1
                while a[j] > pivot: j -= 1
                if i <= j:
                    a[i], a[j] = a[j], a[i]
                    i += 1
                    j -= 1
            _qs(a, lo, j)
            _qs(a, i, hi)
    _qs(arr, 0, len(arr) - 1)
    return arr


sizes = [10000, 50000, 100000, 500000]

print(f"  Random integers in [0, n×100)")
print()
print(f"  {'n':>8s}  {'Counting':>10s}  {'Radix-10':>10s}  {'Radix-256':>10s}  {'Quicksort':>10s}  {'Tim':>8s}")
print(f"  {'─'*8}  {'─'*10}  {'─'*10}  {'─'*10}  {'─'*10}  {'─'*8}")

random.seed(42)
for n in sizes:
    data = [random.randint(0, n * 100) for _ in range(n)]

    t0 = time.perf_counter()
    counting_sort_simple(data, max_val=n * 100)
    t_count = time.perf_counter() - t0

    t0 = time.perf_counter()
    lsd_radix_sort(data, base=10)
    t_r10 = time.perf_counter() - t0

    t0 = time.perf_counter()
    lsd_radix_sort(data, base=256)
    t_r256 = time.perf_counter() - t0

    t0 = time.perf_counter()
    quicksort_bench(data) if n <= 100000 else None
    t_quick = time.perf_counter() - t0 if n <= 100000 else None

    d = data[:]
    t0 = time.perf_counter()
    d.sort()
    t_py = time.perf_counter() - t0

    qs_str = f"{t_quick:.4f}s" if t_quick else " (skip)"
    print(f"  {n:>8d}  {t_count:>9.4f}s  {t_r10:>9.4f}s  {t_r256:>9.4f}s  {qs_str:>10s}  {t_py:>7.4f}s")

print()
print("  Key observations:")
print("  • Counting sort: fastest when range is reasonable, but O(k) memory")
print("  • Radix-256: excellent performance, scales linearly")
print("  • Quicksort: good but O(n log n) — the log factor shows at large n")
print("  • Python sort: C-optimized Timsort holds its own against pure Python radix")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  THE TRADEOFF TABLE
# ─────────────────────────────────────────────────────────────────────────────

section("THE TRADEOFF — There's No Free Lunch")

print("""\
  Non-comparison sorts are O(n), but they pay for it:

  ┌──────────────────┬────────────┬────────────┬──────────────────────────┐
  │ Algorithm        │ Time       │ Space      │ Requires                 │
  ├──────────────────┼────────────┼────────────┼──────────────────────────┤
  │ Counting Sort    │ O(n + k)   │ O(n + k)   │ Integer keys in [0, k]  │
  │ LSD Radix Sort   │ O(d(n+b))  │ O(n + b)   │ Fixed-length keys       │
  │ MSD Radix Sort   │ O(d(n+b))  │ O(n + b)   │ Variable-length OK      │
  │ Bucket Sort      │ O(n) exp.  │ O(n + k)   │ Uniform distribution    │
  └──────────────────┴────────────┴────────────┴──────────────────────────┘

  k = value range, d = number of digits, b = base (radix)

  When these conditions hold, non-comparison sorts dominate.
  When they don't (arbitrary objects, complex comparison functions,
  unknown distribution), comparison sorts are the only option.

  The wisdom: know your data. The right algorithm for the right situation.
  Sometimes that means O(n log n) merge sort. Sometimes O(n) radix sort.
  Sometimes O(n²) insertion sort on 10 elements beats everything.

  Next up: what happens when you combine the best of all worlds?
""")

print("  ─── End of Script 04 ───")
print()
