#!/usr/bin/env python3
"""
02_divide_and_conquer.py — Split, Solve, Merge

The naive sorts all share a fatal flaw: they compare elements one pair at a
time, grinding through every combination. O(n²) — it's like checking a phone
book by reading every name.

But what if you could split the problem in half, sort each half, and combine?
You'd do roughly n comparisons to split/merge, and you'd only split log₂(n)
times before you hit single elements. That's n × log₂(n) — astronomically
faster.

This script covers the two most important sorting algorithms ever discovered,
the mathematical proof that they're optimal (up to constants), and the
information-theoretic argument that comparison-based sorting *cannot* do better.

Topics: merge sort · quicksort · partition schemes · pivot strategies · recurrence
relations · the Master Theorem · the O(n log n) barrier · the tree of comparisons
"""

import random
import time
import math
import sys

sys.setrecursionlimit(50000)

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
#  MERGE SORT — The Reliable Champion
# ─────────────────────────────────────────────────────────────────────────────

section("MERGE SORT — The Reliable Champion")

print("""\
  John von Neumann, 1945. Yes, that von Neumann — the architect of the
  modern computer, the creator of game theory, and one of the contributors
  to the Manhattan Project. In one of its first programs, he wrote merge sort
  for one of the world's first stored-program computers.

  The idea is pure divide and conquer:
    1. Split the array in half
    2. Recursively sort each half
    3. Merge the two sorted halves into one sorted whole

  Step 3 is the key insight: merging two sorted arrays takes O(n) time.
  You just walk two pointers, always picking the smaller head element.

  The result: O(n log n) in ALL cases — best, average, and worst.
  No quadratic catastrophe. No bad pivot luck. Just consistent,
  guaranteed performance.

  The tradeoff: it needs O(n) extra space for the merge buffer.
""")

print("  The Algorithm:")
print("  ─────────────")
print("""\
  def merge_sort(arr):
      if len(arr) <= 1:
          return arr
      mid = len(arr) // 2
      left = merge_sort(arr[:mid])
      right = merge_sort(arr[mid:])
      return merge(left, right)

  def merge(left, right):
      result = []
      i = j = 0
      while i < len(left) and j < len(right):
          if left[i] <= right[j]:     # ≤ for stability
              result.append(left[i])
              i += 1
          else:
              result.append(right[j])
              j += 1
      result.extend(left[i:])
      result.extend(right[j:])
      return result
""")


# Traced merge sort
merge_comparisons = 0
merge_depth_trace = []

def merge_sort_traced(arr, depth=0):
    """Merge sort with comparison counting and recursion tracing."""
    global merge_comparisons
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    merge_depth_trace.append(("split", depth, arr[:], arr[:mid], arr[mid:]))

    left = merge_sort_traced(arr[:mid], depth + 1)
    right = merge_sort_traced(arr[mid:], depth + 1)

    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        merge_comparisons += 1
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])

    merge_depth_trace.append(("merge", depth, result, left, right))
    return result


subsection("Visualizing the Recursion Tree")

demo = [38, 27, 43, 3, 9, 82, 10]
print(f"  Input: {demo}")
print()

merge_comparisons = 0
merge_depth_trace = []
result = merge_sort_traced(demo)

print("  Recursion trace (split phase, then merge phase):")
print()
for action, depth, arr, left, right in merge_depth_trace:
    indent = "    " + "  " * depth
    if action == "split":
        print(f"{indent}Split: {arr} → {left} | {right}")
    else:
        print(f"{indent}Merge: {left} + {right} → {arr}")

print()
print(f"  Result: {result}")
print(f"  Total comparisons: {merge_comparisons}")
print(f"  Theory: n⌈lg n⌉ - 2^⌈lg n⌉ + 1 ≈ {len(demo) * math.ceil(math.log2(len(demo)))}")
print()


subsection("The Merge Step: Why It's O(n)")

print("""\
  The merge of two sorted halves is elegant. Watch the two pointers:

  Left:   [3, 27, 38, 43]          Right: [9, 10, 82]
           ↑ i                              ↑ j

  Compare 3 vs 9: take 3.    Result: [3]
  Compare 27 vs 9: take 9.   Result: [3, 9]
  Compare 27 vs 10: take 10. Result: [3, 9, 10]
  Compare 27 vs 82: take 27. Result: [3, 9, 10, 27]
  Compare 38 vs 82: take 38. Result: [3, 9, 10, 27, 38]
  Compare 43 vs 82: take 43. Result: [3, 9, 10, 27, 38, 43]
  Right exhausted? Append remaining left:  Result: [3, 9, 10, 27, 38, 43, 82]

  Each element is touched exactly once. That's O(n) per merge level,
  and there are O(log n) levels. Total: O(n log n).
""")


# ─────────────────────────────────────────────────────────────────────────────
#  QUICKSORT — The Pragmatic Gambler
# ─────────────────────────────────────────────────────────────────────────────

section("QUICKSORT — The Pragmatic Gambler")

print("""\
  Tony Hoare, 1960. A British computer scientist trying to sort words for
  a machine translation project. He invented quicksort and later said it was
  the best algorithm he ever designed.

  The idea:
    1. Pick a "pivot" element
    2. Partition: everything < pivot goes left, everything > pivot goes right
    3. Recursively sort left and right

  Unlike merge sort, the hard work happens BEFORE the recursion (partitioning),
  not after (merging). And unlike merge sort, quicksort sorts in place — no
  extra O(n) buffer needed.

  The catch: pivot choice matters. A bad pivot gives O(n²). A good pivot
  gives O(n log n). On average, with random data, it's O(n log n) with a
  smaller constant than merge sort — which is why it's the default sort in
  most standard libraries (or was, before hybrids like Timsort and Introsort).
""")


def quicksort_lomuto(arr, lo=0, hi=None, stats=None):
    """Quicksort with Lomuto partition scheme."""
    if hi is None:
        hi = len(arr) - 1
    if stats is None:
        stats = [0, 0]  # [comparisons, swaps]
    if lo < hi:
        pivot = arr[hi]
        i = lo - 1
        for j in range(lo, hi):
            stats[0] += 1
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
                stats[1] += 1
        arr[i + 1], arr[hi] = arr[hi], arr[i + 1]
        stats[1] += 1
        p = i + 1
        quicksort_lomuto(arr, lo, p - 1, stats)
        quicksort_lomuto(arr, p + 1, hi, stats)
    return stats


def quicksort_hoare(arr, lo=0, hi=None, stats=None):
    """Quicksort with Hoare partition scheme (original, fewer swaps)."""
    if hi is None:
        hi = len(arr) - 1
    if stats is None:
        stats = [0, 0]
    if lo < hi:
        pivot = arr[(lo + hi) // 2]
        i = lo - 1
        j = hi + 1
        while True:
            i += 1
            while arr[i] < pivot:
                stats[0] += 1
                i += 1
            stats[0] += 1
            j -= 1
            while arr[j] > pivot:
                stats[0] += 1
                j -= 1
            stats[0] += 1
            if i >= j:
                break
            arr[i], arr[j] = arr[j], arr[i]
            stats[1] += 1
        quicksort_hoare(arr, lo, j, stats)
        quicksort_hoare(arr, j + 1, hi, stats)
    return stats


subsection("Lomuto vs. Hoare Partitioning")

print("""\
  LOMUTO (textbook version):
    Pivot = last element. Walk left-to-right, swap small elements to front.
    Simple to understand, but does more swaps than necessary.

  HOARE (original version):
    Pivot = middle element. Two pointers walk inward from each end.
    Fewer swaps, but trickier to implement correctly.
    Most production implementations use Hoare (or a variant).
""")

random.seed(42)
n = 5000
data = random.sample(range(n * 10), n)

data_l = data[:]
data_h = data[:]
stats_l = quicksort_lomuto(data_l)
stats_h = quicksort_hoare(data_h)

print(f"  n = {n}, random data:")
print(f"  Lomuto: {stats_l[0]:>8d} comparisons, {stats_l[1]:>8d} swaps")
print(f"  Hoare:  {stats_h[0]:>8d} comparisons, {stats_h[1]:>8d} swaps")
print(f"  Hoare uses ~3× fewer swaps — that was Hoare's original insight.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  PIVOT STRATEGY: THE MAKE-OR-BREAK DECISION
# ─────────────────────────────────────────────────────────────────────────────

section("PIVOT STRATEGY: THE MAKE-OR-BREAK DECISION")

print("""\
  Quicksort's performance hinges on pivot quality. The ideal pivot splits
  the array exactly in half. The worst pivot is the min or max — giving
  one empty partition and one of size n-1. That's O(n²).

  Common strategies:
    • First/last element:  Fast, but O(n²) on sorted/reversed data (!!)
    • Random element:      O(n log n) expected. Can't be adversarially attacked.
    • Median of three:     Take first, middle, last — use the median as pivot.
                           Cheap and effective. Used in most implementations.
    • Ninther:             Median of three medians-of-three. Used for large arrays.

  Let's see how pivot choice affects performance:
""")


def quicksort_first_pivot(arr, lo=0, hi=None, stats=None):
    """Quicksort with first-element pivot (vulnerable to sorted data)."""
    if hi is None:
        hi = len(arr) - 1
    if stats is None:
        stats = [0, 0]
    if lo < hi:
        pivot = arr[lo]
        i = lo + 1
        for j in range(lo + 1, hi + 1):
            stats[0] += 1
            if arr[j] < pivot:
                arr[i], arr[j] = arr[j], arr[i]
                stats[1] += 1
                i += 1
        arr[lo], arr[i - 1] = arr[i - 1], arr[lo]
        stats[1] += 1
        p = i - 1
        quicksort_first_pivot(arr, lo, p - 1, stats)
        quicksort_first_pivot(arr, p + 1, hi, stats)
    return stats


def quicksort_median3(arr, lo=0, hi=None, stats=None):
    """Quicksort with median-of-three pivot selection."""
    if hi is None:
        hi = len(arr) - 1
    if stats is None:
        stats = [0, 0]
    if lo < hi:
        # Median of three
        mid = (lo + hi) // 2
        if arr[lo] > arr[mid]:
            arr[lo], arr[mid] = arr[mid], arr[lo]
        if arr[lo] > arr[hi]:
            arr[lo], arr[hi] = arr[hi], arr[lo]
        if arr[mid] > arr[hi]:
            arr[mid], arr[hi] = arr[hi], arr[mid]
        # Place pivot at hi-1
        arr[mid], arr[hi - 1] = arr[hi - 1], arr[mid]
        pivot = arr[hi - 1]

        i = lo
        j = hi - 1
        while True:
            i += 1
            while arr[i] < pivot:
                stats[0] += 1
                i += 1
            stats[0] += 1
            j -= 1
            while arr[j] > pivot:
                stats[0] += 1
                j -= 1
            stats[0] += 1
            if i >= j:
                break
            arr[i], arr[j] = arr[j], arr[i]
            stats[1] += 1
        arr[i], arr[hi - 1] = arr[hi - 1], arr[i]
        stats[1] += 1

        quicksort_median3(arr, lo, i - 1, stats)
        quicksort_median3(arr, i + 1, hi, stats)
    return stats


n = 3000  # Smaller to avoid stack overflow with bad pivots
patterns = [
    ("Random",        lambda: random.sample(range(n * 10), n)),
    ("Nearly sorted", lambda: sorted(range(n))[:n-10] + random.sample(range(n), 10)),
    ("Few unique",    lambda: [random.randint(0, 9) for _ in range(n)]),
]

print(f"  n = {n}")
print()
print(f"  {'Pattern':>16s}  {'First pivot':>16s}  {'Median-of-3':>16s}  {'Hoare mid':>16s}")
print(f"  {'─'*16}  {'─'*16}  {'─'*16}  {'─'*16}")

for label, gen in patterns:
    data = gen()
    d1, d2, d3 = data[:], data[:], data[:]

    s1 = quicksort_first_pivot(d1)
    s3 = quicksort_median3(d2) if label != "Nearly sorted" else [0, 0]
    s2 = quicksort_hoare(d3)

    c1, c2, c3 = s1[0], s2[0], s3[0]
    print(f"  {label:>16s}  {c1:>12d} cmp  {c3:>12d} cmp  {c2:>12d} cmp")

print()
print("  First-pivot quicksort on sorted data is a disaster (O(n²)).")
print("  Median-of-three and Hoare-with-mid tame the worst case effectively.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  MERGE SORT VS. QUICKSORT: HEAD TO HEAD
# ─────────────────────────────────────────────────────────────────────────────

section("MERGE SORT VS. QUICKSORT — HEAD TO HEAD")

print("""\
  Both are O(n log n) on average. But they make different tradeoffs:

  ┌─────────────────┬─────────────────────┬─────────────────────┐
  │                 │    Merge Sort        │    Quicksort        │
  ├─────────────────┼─────────────────────┼─────────────────────┤
  │ Worst case      │  O(n log n) always   │  O(n²) with bad     │
  │                 │                      │  pivot (rare)        │
  │ Memory          │  O(n) extra          │  O(log n) stack      │
  │ Stable?         │  Yes                 │  No (standard)       │
  │ Cache behavior  │  Sequential merges   │  In-place ≈ better   │
  │ Const factor    │  Higher              │  Lower               │
  │ Parallelism     │  Excellent           │  Good                │
  │ External sort   │  Perfect             │  Difficult           │
  └─────────────────┴─────────────────────┴─────────────────────┘

  In practice, quicksort wins on random data in RAM (cache efficiency).
  Merge sort wins when stability matters, when worst-case guarantees are
  needed, or when data doesn't fit in memory (external sorting).
""")


def merge_sort_simple(arr):
    """Simple merge sort for benchmarking."""
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort_simple(arr[:mid])
    right = merge_sort_simple(arr[mid:])
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def quicksort_bench(arr):
    """Quicksort for benchmarking (Hoare, in-place)."""
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
    arr = arr[:]
    _qs(arr, 0, len(arr) - 1)
    return arr


sizes_race = [1000, 5000, 10000, 50000, 100000]

print(f"  {'n':>8s}  {'Merge Sort':>12s}  {'Quicksort':>12s}  {'Python sort':>12s}")
print(f"  {'─'*8}  {'─'*12}  {'─'*12}  {'─'*12}")

for n in sizes_race:
    data = random.sample(range(n * 10), n)

    t0 = time.perf_counter()
    merge_sort_simple(data)
    t_merge = time.perf_counter() - t0

    t0 = time.perf_counter()
    quicksort_bench(data)
    t_quick = time.perf_counter() - t0

    data_py = data[:]
    t0 = time.perf_counter()
    data_py.sort()
    t_python = time.perf_counter() - t0

    print(f"  {n:>8d}  {t_merge:>11.4f}s  {t_quick:>11.4f}s  {t_python:>11.4f}s")

print()
print("  Python's built-in sort (Timsort) crushes both — it's a C-optimized hybrid.")
print("  Our pure Python implementations show the algorithmic comparison.")
print("  The key insight: both scale as n log n, while naive sorts would be n².")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  RECURRENCE RELATIONS & THE MASTER THEOREM
# ─────────────────────────────────────────────────────────────────────────────

section("RECURRENCE RELATIONS & THE MASTER THEOREM")

print("""\
  Why is merge sort O(n log n)? Let T(n) be the time to sort n elements.

  T(n) = 2·T(n/2) + O(n)
         ─────────   ────
         two halves   merge step

  This is a RECURRENCE RELATION. To solve it, we use the Master Theorem:

  For T(n) = a·T(n/b) + O(n^d):
    • If d > log_b(a): T(n) = O(n^d)
    • If d = log_b(a): T(n) = O(n^d · log n)
    • If d < log_b(a): T(n) = O(n^(log_b a))

  Merge sort: a=2, b=2, d=1 → log₂(2) = 1 = d → Case 2 → O(n log n) ✓

  Quicksort (balanced): Same recurrence → O(n log n) ✓
  Quicksort (worst):    T(n) = T(n-1) + O(n) → O(n²) ✗

  The tree view makes it intuitive:
""")

print("""\
  Merge sort recursion tree (n=16):

  Level 0:  [────────────────16────────────────]     n work
  Level 1:  [────────8────────] [────────8────────]  n work
  Level 2:  [───4───] [───4───] [───4───] [───4───]  n work
  Level 3:  [─2─][─2─] [─2─][─2─] [─2─][─2─] [─2─][─2─]  n work
  Level 4:  1 1  1 1   1 1  1 1   1 1  1 1   1 1  1 1

  Each level does O(n) total work (merging). There are log₂(n) levels.
  Total: O(n) × O(log n) = O(n log n).

  Quicksort (worst-case) recursion tree:

  Level 0:  [────────────────16────────────────]     n work
  Level 1:  [0] [──────────────15──────────────]     n-1 work
  Level 2:  [0] [────────────14────────────]          n-2 work
  Level 3:  [0] [──────────13──────────]              n-3 work
  ...                                                  ...

  n levels × O(n) each = O(n²). This happens when pivot is always min or max.
""")


# ─────────────────────────────────────────────────────────────────────────────
#  THE INFORMATION-THEORETIC LOWER BOUND
# ─────────────────────────────────────────────────────────────────────────────

section("THE O(n log n) BARRIER — WHY YOU CAN'T DO BETTER")

print("""\
  Here's one of the most beautiful proofs in computer science.

  Theorem: Any comparison-based sorting algorithm must make at least
           ⌈log₂(n!)⌉ comparisons in the worst case.

  Proof sketch:
    • There are n! possible orderings of n elements.
    • Before sorting, we don't know which ordering we have.
    • Each comparison is a yes/no question that eliminates at most
      half the possibilities.
    • To distinguish among n! orderings, we need at least log₂(n!)
      yes/no questions.

  By Stirling's approximation:
    log₂(n!) ≈ n·log₂(n) - n·log₂(e) ≈ n·log₂(n) - 1.443n

  So Ω(n log n) is a LOWER BOUND. No comparison sort can beat it.

  This is called the DECISION TREE argument:
""")

print("""\
  Decision tree for sorting [a, b, c] (3! = 6 possible orderings):

                     a < b?
                    /      \\
                 yes        no
                /              \\
            b < c?            a < c?
           /     \\           /     \\
        yes       no       yes      no
        /           \\       /         \\
  [a,b,c]       a < c?  [b,a,c]    b < c?
                /    \\              /    \\
             yes      no         yes     no
             /          \\         /        \\
        [a,c,b]     [c,a,b]  [b,c,a]   [c,b,a]

  6 leaf nodes (= 3! permutations). Tree height = 3 = ⌈log₂(6)⌉.
  Any comparison sort of 3 elements needs at least 3 comparisons
  in the worst case.
""")

# Verify with actual numbers
print("  The lower bound for various n:")
print()
print(f"  {'n':>6s}  {'n!':>20s}  {'⌈log₂(n!)⌉':>12s}  {'n⌈log₂(n)⌉':>12s}")
print(f"  {'─'*6}  {'─'*20}  {'─'*12}  {'─'*12}")

for n in [3, 5, 8, 10, 20, 100]:
    nfact = math.factorial(n)
    lb = math.ceil(math.log2(nfact)) if nfact > 0 else 0
    nlgn = n * math.ceil(math.log2(n)) if n > 1 else 0
    nfact_str = str(nfact) if nfact < 10**18 else f"≈10^{math.log10(nfact):.1f}"
    print(f"  {n:>6d}  {nfact_str:>20s}  {lb:>12d}  {nlgn:>12d}")

print()
print("  Merge sort achieves roughly n⌈log₂(n)⌉ comparisons — within a")
print("  small constant of optimal. It's TIGHT.")
print()
print("  The lower bound says: comparison sorts CANNOT beat O(n log n).")
print("  But Script 04 will show: non-comparison sorts CAN. Stay tuned.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  COUNTING MERGE SORT INVERSIONS — A BONUS POWER
# ─────────────────────────────────────────────────────────────────────────────

section("BONUS: COUNTING INVERSIONS IN O(n log n)")

print("""\
  In Script 01, we counted inversions in O(n²). But merge sort can count
  them in O(n log n) — for free!

  During the merge step, when we take an element from the RIGHT half
  (because it's smaller than the current LEFT element), every remaining
  element in the LEFT half forms an inversion with it. That's a batch
  count in O(1).

  This is used in the real world for:
    • Kendall tau distance (how different are two rankings?)
    • Collaborative filtering (how similar are two users' preferences?)
    • Measuring the "sortedness" of a sequence
""")


def merge_sort_count_inversions(arr):
    """Merge sort that also counts inversions: O(n log n)."""
    if len(arr) <= 1:
        return arr, 0

    mid = len(arr) // 2
    left, left_inv = merge_sort_count_inversions(arr[:mid])
    right, right_inv = merge_sort_count_inversions(arr[mid:])

    merged = []
    inversions = left_inv + right_inv
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            inversions += len(left) - i  # All remaining left elements are inversions
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged, inversions


test_cases = [
    [1, 2, 3, 4, 5],
    [5, 4, 3, 2, 1],
    [3, 1, 4, 1, 5],
    [2, 4, 1, 3, 5],
]

print(f"  {'Array':>24s}  {'Inversions (O(n²))':>18s}  {'Inversions (merge)':>18s}")
print(f"  {'─'*24}  {'─'*18}  {'─'*18}")

for arr in test_cases:
    # Brute force for verification
    n = len(arr)
    brute = sum(1 for i in range(n) for j in range(i+1, n) if arr[i] > arr[j])
    _, merge_inv = merge_sort_count_inversions(arr)
    match = "✓" if brute == merge_inv else "✗"
    print(f"  {str(arr):>24s}  {brute:>18d}  {merge_inv:>18d}  {match}")

print()

# Large-scale demonstration
random.seed(42)
big = random.sample(range(100000), 10000)
_, big_inv = merge_sort_count_inversions(big)
max_inv = 10000 * 9999 // 2
print(f"  Random array (n=10,000): {big_inv:,} inversions out of {max_inv:,} maximum")
print(f"  Ratio: {big_inv/max_inv:.4f} ≈ 0.25 (expected for random permutation: 1/4)")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  THE n log n SCALING: SEEING IT IN THE NUMBERS
# ─────────────────────────────────────────────────────────────────────────────

section("SEEING n log n IN THE NUMBERS")

print("""\
  Let's verify: when n doubles, merge sort time should grow by
  roughly 2× + a little more (the extra log factor). Compare with
  O(n²) which would quadruple.
""")

from functools import wraps

def insertion_sort_bench(arr):
    arr = arr[:]
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr


sizes = [1000, 2000, 4000, 8000, 16000]

print(f"  {'n':>8s}  {'Insertion ':>10s}  {'Ratio':>6s}  {'Merge ':>10s}  {'Ratio':>6s}  {'Quick ':>10s}  {'Ratio':>6s}")
print(f"  {'─'*8}  {'─'*10}  {'─'*6}  {'─'*10}  {'─'*6}  {'─'*10}  {'─'*6}")

prev_ins = prev_merge = prev_quick = None
for n in sizes:
    data = random.sample(range(n * 10), n)

    if n <= 8000:
        t0 = time.perf_counter()
        insertion_sort_bench(data)
        t_ins = time.perf_counter() - t0
    else:
        t_ins = None

    t0 = time.perf_counter()
    merge_sort_simple(data)
    t_merge = time.perf_counter() - t0

    t0 = time.perf_counter()
    quicksort_bench(data)
    t_quick = time.perf_counter() - t0

    ins_str = f"{t_ins:.4f}s" if t_ins else "  (skip)"
    ins_ratio = f"{t_ins/prev_ins:.2f}×" if (prev_ins and t_ins) else "  —"
    merge_ratio = f"{t_merge/prev_merge:.2f}×" if prev_merge else "  —"
    quick_ratio = f"{t_quick/prev_quick:.2f}×" if prev_quick else "  —"

    print(f"  {n:>8d}  {ins_str:>10s}  {ins_ratio:>6s}  {t_merge:>9.4f}s  {merge_ratio:>6s}  {t_quick:>9.4f}s  {quick_ratio:>6s}")

    if t_ins:
        prev_ins = t_ins
    prev_merge = t_merge
    prev_quick = t_quick

print()
print("  Insertion sort: ratio ≈ 4× when n doubles → O(n²) confirmed")
print("  Merge/Quicksort: ratio ≈ 2.2× when n doubles → O(n log n) confirmed")
print("  (The extra 0.2 over 2× comes from the log factor growing slowly)")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  THREE-WAY QUICKSORT (DUTCH NATIONAL FLAG)
# ─────────────────────────────────────────────────────────────────────────────

section("THREE-WAY QUICKSORT — The Dutch National Flag")

print("""\
  Standard quicksort partitions into < pivot and ≥ pivot. If there are many
  duplicates, the ≥ partition keeps re-sorting equal elements needlessly.

  Dijkstra's Dutch National Flag partition splits into THREE groups:
    < pivot  |  = pivot  |  > pivot

  Equal elements go straight to their final position. With many duplicates,
  this turns O(n²) Lomuto quicksort into O(n log n) three-way quicksort.

  Named after the flag of the Netherlands: red | white | blue — three bands.

  Edsger Dijkstra: the same person who gave us Dijkstra's algorithm for
  shortest paths [← repo 3]. He really gets around.
""")


def quicksort_3way(arr, lo=0, hi=None, stats=None):
    """Three-way quicksort (Dutch National Flag partition)."""
    if hi is None:
        hi = len(arr) - 1
    if stats is None:
        stats = [0, 0]
    if lo >= hi:
        return stats

    pivot = arr[lo]
    lt, gt = lo, hi
    i = lo + 1

    while i <= gt:
        stats[0] += 1
        if arr[i] < pivot:
            arr[lt], arr[i] = arr[i], arr[lt]
            stats[1] += 1
            lt += 1
            i += 1
        elif arr[i] > pivot:
            arr[i], arr[gt] = arr[gt], arr[i]
            stats[1] += 1
            gt -= 1
        else:
            i += 1

    # arr[lo..lt-1] < pivot, arr[lt..gt] = pivot, arr[gt+1..hi] > pivot
    quicksort_3way(arr, lo, lt - 1, stats)
    quicksort_3way(arr, gt + 1, hi, stats)
    return stats


# Compare on data with many duplicates
n = 10000
data_few = [random.randint(0, 9) for _ in range(n)]

d1, d2 = data_few[:], data_few[:]
s_lomuto = quicksort_lomuto(d1)
s_3way = quicksort_3way(d2)

print(f"  n = {n}, values in [0, 9] (many duplicates):")
print(f"  Lomuto quicksort:   {s_lomuto[0]:>10d} comparisons")
print(f"  Three-way quicksort:{s_3way[0]:>10d} comparisons")
print(f"  Three-way is {s_lomuto[0]/s_3way[0]:.1f}× fewer comparisons with many duplicates.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

section("DIVIDE AND CONQUER: SUMMARY")

print("""\
  ┌─────────────────┬──────────┬──────────┬──────────┬────────┬────────┐
  │ Algorithm       │  Best    │ Average  │  Worst   │ Memory │ Stable │
  ├─────────────────┼──────────┼──────────┼──────────┼────────┼────────┤
  │ Merge Sort      │O(n lg n) │O(n lg n) │O(n lg n) │  O(n)  │  Yes   │
  │ Quicksort       │O(n lg n) │O(n lg n) │  O(n²)   │O(lg n) │  No    │
  │ 3-Way Quicksort │  O(n)    │O(n lg n) │  O(n²)*  │O(lg n) │  No    │
  └─────────────────┴──────────┴──────────┴──────────┴────────┴────────┘

  * 3-way quicksort worst case is still O(n²) but only with pathological
    pivot choices AND all distinct elements. With duplicates, it's often O(n).

  Key takeaways:
  • Merge sort: guaranteed O(n log n), stable, but needs O(n) memory.
  • Quicksort: fastest in practice on random data, but O(n²) worst case.
  • Pivot strategy is critical — median-of-three kills the worst case.
  • Three-way partition handles duplicates gracefully.
  • O(n log n) is the theoretical floor for comparison sorts.

  Next up: heapsort — sorting with a tree structure baked into an array.
""")

print("  ─── End of Script 02 ───")
print()
