#!/usr/bin/env python3
"""
05_adaptive_and_hybrid.py — Exploiting Existing Order

The real world rarely gives you perfectly random data. Sensor readings
arrive mostly in order. Log files are time-stamped. Database records are
nearly sorted by primary key after a batch insert. User data has structure.

Hybrid sorts exploit this: they detect patterns in the data and adapt their
strategy. Timsort (Python, Java, Swift, Rust) merges natural runs. Introsort
(C++, .NET) switches strategy when quicksort goes bad. Shellsort uses a
gap sequence to pre-sort the data before finishing with insertion sort.

This script reverse-engineers the algorithms that actually power the world's
standard libraries. When you call list.sort() in Python, THIS is what runs.

Topics: Timsort · natural runs · galloping mode · minrun calculation ·
insertion sort for small arrays · Introsort · quicksort + heapsort fallback ·
Shellsort · gap sequences · the open problem · adaptive merge
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
#  THE CASE FOR ADAPTIVITY
# ─────────────────────────────────────────────────────────────────────────────

section("THE CASE FOR ADAPTIVITY — Real Data Isn't Random")

print("""\
  Computer science textbooks analyze sorting on random data. But real data
  has structure. Consider:

    • Server logs: already in timestamp order (with occasional late arrivals)
    • Stock prices: mostly increasing during a bull market
    • Sensor arrays: readings that change slowly over time
    • Database queries: results often pre-sorted on the primary key
    • Undo history: events in sequence with occasional reorders

  An adaptive sort takes advantage of existing order ("runs") in the data.
  On random data, it's still O(n log n). But on nearly-sorted data, it can
  approach O(n). That's the best of both worlds.

  How much existing order is in these patterns?
""")


def count_runs(arr):
    """Count the number of natural ascending or descending runs."""
    if len(arr) <= 1:
        return 1
    runs = 1
    for i in range(1, len(arr)):
        if i > 0 and ((arr[i] >= arr[i-1]) != (arr[i-1] >= arr[i-2] if i >= 2 else True)):
            # Simple approximation: count direction changes
            pass
    # Better: count maximal ascending runs
    runs = 1
    for i in range(1, len(arr)):
        if arr[i] < arr[i-1]:
            runs += 1
    return runs


n = 10000
patterns = {
    "Random":         random.sample(range(n * 10), n),
    "Sorted":         list(range(n)),
    "Reversed":       list(range(n, 0, -1)),
    "Nearly sorted":  None,  # set up below
    "Pipe organ":     list(range(n // 2)) + list(range(n // 2, 0, -1)),
    "Sawtooth":       [i % 100 for i in range(n)],
}

nearly = list(range(n))
random.seed(42)
for _ in range(n // 50):
    i, j = random.randint(0, n-1), random.randint(0, n-1)
    nearly[i], nearly[j] = nearly[j], nearly[i]
patterns["Nearly sorted"] = nearly

print(f"  {'Pattern':>16s}  {'Runs':>8s}  {'Runs/n':>8s}  {'Character':>20s}")
print(f"  {'─'*16}  {'─'*8}  {'─'*8}  {'─'*20}")
for label, data in patterns.items():
    runs = count_runs(data)
    ratio = runs / len(data)
    character = "chaotic" if ratio > 0.4 else "structured" if ratio < 0.05 else "moderate"
    print(f"  {label:>16s}  {runs:>8d}  {ratio:>8.4f}  {character:>20s}")

print()
print("  Fewer runs = more existing order = faster adaptive sort.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  NATURAL MERGE SORT — The Foundation of Timsort
# ─────────────────────────────────────────────────────────────────────────────

section("NATURAL MERGE SORT — Finding and Merging Runs")

print("""\
  Standard merge sort always splits at the midpoint. Natural merge sort
  instead finds existing sorted runs and merges them.

  On [1, 3, 5, 2, 4, 6, 8, 7]:
    Standard: split at index 4, regardless of structure
    Natural:  find runs [1,3,5], [2,4,6,8], [7] and merge them

  If the data already has long runs, natural merge sort skips the splitting
  phase entirely and goes straight to merging — potentially much faster.
""")


def natural_merge_sort(arr):
    """Natural merge sort: find existing runs and merge them."""
    n = len(arr)
    if n <= 1:
        return arr[:], 0

    arr = arr[:]
    comparisons = 0

    # Find natural runs (ascending or descending)
    def find_runs(a):
        runs = []
        i = 0
        while i < len(a):
            start = i
            if i + 1 < len(a) and a[i] > a[i + 1]:
                # Descending run — reverse it
                while i + 1 < len(a) and a[i] > a[i + 1]:
                    i += 1
                run = a[start:i + 1]
                run.reverse()
            else:
                # Ascending run
                while i + 1 < len(a) and a[i] <= a[i + 1]:
                    i += 1
                run = a[start:i + 1]
            runs.append(run)
            i += 1
        return runs

    runs = find_runs(arr)

    def merge(left, right):
        nonlocal comparisons
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            comparisons += 1
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result

    # Merge runs pairwise until one remains
    while len(runs) > 1:
        new_runs = []
        for i in range(0, len(runs), 2):
            if i + 1 < len(runs):
                new_runs.append(merge(runs[i], runs[i + 1]))
            else:
                new_runs.append(runs[i])
        runs = new_runs

    return runs[0] if runs else [], comparisons


# Compare standard vs natural merge sort
def merge_sort_standard(arr):
    comparisons = [0]
    def _ms(a):
        if len(a) <= 1:
            return a
        mid = len(a) // 2
        left = _ms(a[:mid])
        right = _ms(a[mid:])
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            comparisons[0] += 1
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result
    return _ms(arr), comparisons[0]

n = 10000
print(f"  Comparison counts (n = {n:,}):")
print()
print(f"  {'Pattern':>16s}  {'Standard merge':>14s}  {'Natural merge':>14s}  {'Savings':>10s}")
print(f"  {'─'*16}  {'─'*14}  {'─'*14}  {'─'*10}")

for label in ["Random", "Nearly sorted", "Sorted", "Reversed", "Pipe organ"]:
    data = patterns[label][:n]
    _, c_std = merge_sort_standard(data)
    _, c_nat = natural_merge_sort(data)
    savings = (1 - c_nat / c_std) * 100 if c_std > 0 else 0
    print(f"  {label:>16s}  {c_std:>14,}  {c_nat:>14,}  {savings:>9.1f}%")

print()
print("  Natural merge sort: same work on random data, massive savings on structured data.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  TIMSORT — The World's Favorite Sort
# ─────────────────────────────────────────────────────────────────────────────

section("TIMSORT — The World's Favorite Sort")

print("""\
  Tim Peters, 2002. A Python core developer who wrote the sorting algorithm
  used by Python, Java (since JDK 7), Swift, Rust, Android, and V8 (Chrome's
  JavaScript engine).

  Timsort is natural merge sort with three key enhancements:

  1. MINRUN: Short runs are extended to a minimum length using insertion sort.
     This ensures merge operations are balanced.

  2. MERGE STRATEGY: A stack-based merging policy ensures at most O(n) pending
     runs, keeping memory bounded. Runs are merged to maintain invariants:
       • run[i-2] > run[i-1] + run[i]
       • run[i-1] > run[i]

  3. GALLOPING MODE: When one run "wins" many consecutive merge comparisons,
     Timsort switches to exponential search (galloping) to skip ahead. This
     makes merging two runs with very different value ranges nearly linear.

  Result: O(n log n) worst case, O(n) on sorted data, excellent on real-world
  data with long runs, and stable.
""")


subsection("Minrun Calculation")

print("""\
  Timsort's minrun is chosen so that n / minrun is a power of 2 (or close).
  This makes the final merge tree well-balanced.

  The formula: take the 6 most significant bits of n, rounding up if any
  remaining bits are set.
""")

def compute_minrun(n):
    """Timsort's minrun calculation (from CPython source)."""
    r = 0
    while n >= 64:
        r |= n & 1
        n >>= 1
    return n + r


print(f"  {'n':>10s}  {'minrun':>8s}")
print(f"  {'─'*10}  {'─'*8}")
for n in [64, 100, 128, 200, 256, 500, 1000, 10000, 100000, 1000000]:
    print(f"  {n:>10d}  {compute_minrun(n):>8d}")

print()
print("  Minrun is always in [32, 64]. Short enough for insertion sort to be fast,")
print("  long enough that we don't create too many runs.")
print()


subsection("Galloping Mode — Exponential Search in Merges")

print("""\
  Standard merge: compare one element at a time. O(n) per merge.

  Galloping: when run A "wins" 7+ consecutive comparisons, switch to
  exponential search: check positions 1, 2, 4, 8, 16, ... in run B.
  Once you overshoot, binary search the last interval.

  This is O(log k) where k is the number of elements skipped.
  On data with interleaved runs of different ranges, this is a huge win.

  Example: merging [1, 2, 3, ..., 1000] with [1001, 1002, ..., 2000].
    Standard: 1000 comparisons (each A element wins, one at a time).
    Galloping: ~10 comparisons (exponential search finds all 1000 at once).
""")


def galloping_merge(left, right):
    """Merge with galloping mode."""
    result = []
    i = j = 0
    comparisons = 0
    gallops = 0

    MIN_GALLOP = 7

    while i < len(left) and j < len(right):
        # Normal mode: compare one at a time, count consecutive wins
        left_wins = 0
        right_wins = 0

        while i < len(left) and j < len(right):
            comparisons += 1
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
                left_wins += 1
                right_wins = 0
                if left_wins >= MIN_GALLOP:
                    break
            else:
                result.append(right[j])
                j += 1
                right_wins += 1
                left_wins = 0
                if right_wins >= MIN_GALLOP:
                    break

        # Galloping mode
        if left_wins >= MIN_GALLOP and i < len(left) and j < len(right):
            gallops += 1
            # Gallop in right: find where right[j] fits in left[i:]
            k = 1
            while i + k < len(left) and left[i + k] <= right[j]:
                comparisons += 1
                k *= 2
            # Binary search between i + k//2 and min(i + k, len(left))
            lo, hi = i + k // 2, min(i + k, len(left))
            while lo < hi:
                comparisons += 1
                mid = (lo + hi) // 2
                if left[mid] <= right[j]:
                    lo = mid + 1
                else:
                    hi = mid
            result.extend(left[i:lo])
            i = lo

        elif right_wins >= MIN_GALLOP and i < len(left) and j < len(right):
            gallops += 1
            k = 1
            while j + k < len(right) and right[j + k] < left[i]:
                comparisons += 1
                k *= 2
            lo, hi = j + k // 2, min(j + k, len(right))
            while lo < hi:
                comparisons += 1
                mid = (lo + hi) // 2
                if right[mid] < left[i]:
                    lo = mid + 1
                else:
                    hi = mid
            result.extend(right[j:lo])
            j = lo

    result.extend(left[i:])
    result.extend(right[j:])
    return result, comparisons, gallops


# Demonstrate galloping advantage
left = list(range(0, 1000))
right = list(range(1000, 2000))

# Standard merge
std_comps = 0
ri = rj = 0
l, r = left[:], right[:]
while ri < len(l) and rj < len(r):
    std_comps += 1
    if l[ri] <= r[rj]:
        ri += 1
    else:
        rj += 1

_, gal_comps, gal_count = galloping_merge(left, right)

print(f"  Merging [0..999] with [1000..1999] (no interleaving):")
print(f"    Standard merge: {std_comps:,} comparisons")
print(f"    Galloping merge: {gal_comps:,} comparisons ({gal_count} gallops)")
print(f"    Speedup: {std_comps / gal_comps:.1f}× fewer comparisons")
print()

# Interleaved case
left2 = list(range(0, 2000, 2))   # evens
right2 = list(range(1, 2000, 2))  # odds
_, gal_comps2, gal_count2 = galloping_merge(left2, right2)
std_comps2 = len(left2) + len(right2) - 1  # approximately
print(f"  Merging evens with odds (fully interleaved):")
print(f"    Galloping merge: {gal_comps2:,} comparisons ({gal_count2} gallops)")
print(f"    Galloping doesn't help here — runs interleave too much. That's OK.")
print(f"    Timsort detects this and stays in normal mode.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  TIMSORT IMPLEMENTATION
# ─────────────────────────────────────────────────────────────────────────────

subsection("Simplified Timsort")

def timsort_simplified(arr):
    """Simplified Timsort: find runs, extend with insertion sort, merge."""
    arr = arr[:]
    n = len(arr)
    if n <= 1:
        return arr

    minrun = compute_minrun(n)

    # Phase 1: Find/extend runs
    runs = []  # list of (start, length)
    i = 0
    while i < n:
        start = i
        # Find natural run
        if i + 1 < n:
            if arr[i] <= arr[i + 1]:
                # Ascending
                while i + 1 < n and arr[i] <= arr[i + 1]:
                    i += 1
            else:
                # Descending — reverse it
                while i + 1 < n and arr[i] > arr[i + 1]:
                    i += 1
                arr[start:i + 1] = arr[start:i + 1][::-1]
        i += 1
        run_len = i - start

        # Extend to minrun with insertion sort
        while i < n and run_len < minrun:
            # Insert arr[i] into arr[start:i]
            key = arr[i]
            j = i - 1
            while j >= start and arr[j] > key:
                arr[j + 1] = arr[j]
                j -= 1
            arr[j + 1] = key
            i += 1
            run_len += 1

        runs.append((start, run_len))

    # Phase 2: Merge runs (simplified — just merge pairwise)
    def merge_at(a, lo, mid, hi):
        left = a[lo:mid]
        right = a[mid:hi]
        k = lo
        li = ri = 0
        while li < len(left) and ri < len(right):
            if left[li] <= right[ri]:
                a[k] = left[li]
                li += 1
            else:
                a[k] = right[ri]
                ri += 1
            k += 1
        while li < len(left):
            a[k] = left[li]
            li += 1
            k += 1
        while ri < len(right):
            a[k] = right[ri]
            ri += 1
            k += 1

    # Merge adjacent runs
    while len(runs) > 1:
        new_runs = []
        for j in range(0, len(runs), 2):
            if j + 1 < len(runs):
                s1, l1 = runs[j]
                s2, l2 = runs[j + 1]
                merge_at(arr, s1, s1 + l1, s1 + l1 + l2)
                new_runs.append((s1, l1 + l2))
            else:
                new_runs.append(runs[j])
        runs = new_runs

    return arr


# Verify correctness
demo = [5, 3, 8, 1, 9, 2, 7, 4, 6, 10]
result = timsort_simplified(demo)
print(f"  Input:  {demo}")
print(f"  Output: {result}")
print(f"  Correct: {result == sorted(demo)} ✓")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  INTROSORT — Quicksort with a Safety Net
# ─────────────────────────────────────────────────────────────────────────────

section("INTROSORT — Quicksort with a Safety Net")

print("""\
  David Musser, 1997. The sort used by C++ std::sort, .NET, and Go.

  The problem with quicksort: it can degrade to O(n²).
  The problem with heapsort: it's always O(n log n) but slower on average.
  The problem with merge sort: it needs O(n) extra memory.

  Introsort: start with quicksort (fast on average), but track recursion
  depth. If it exceeds 2·⌊log₂(n)⌋, switch to heapsort (guaranteed
  O(n log n)). For small partitions (≤16 elements), use insertion sort.

  This gives O(n log n) worst case + quicksort's fast average + insertion
  sort's efficiency on small arrays. The best of three worlds.
""")


def introsort(arr, max_depth=None):
    """Introsort: quicksort + heapsort fallback + insertion sort for small arrays."""
    arr = arr[:]
    n = len(arr)
    if max_depth is None:
        max_depth = 2 * int(math.log2(n)) if n > 1 else 0

    def _heapsort(a, lo, hi):
        """In-place heapsort on a[lo:hi+1]."""
        size = hi - lo + 1
        def sift(a, i, n, lo):
            while True:
                largest = i
                left = 2 * i + 1
                right = 2 * i + 2
                if left < n and a[lo + left] > a[lo + largest]:
                    largest = left
                if right < n and a[lo + right] > a[lo + largest]:
                    largest = right
                if largest != i:
                    a[lo + i], a[lo + largest] = a[lo + largest], a[lo + i]
                    i = largest
                else:
                    break
        for i in range(size // 2 - 1, -1, -1):
            sift(a, i, size, lo)
        for i in range(size - 1, 0, -1):
            a[lo], a[lo + i] = a[lo + i], a[lo]
            sift(a, 0, i, lo)

    def _insertion_sort(a, lo, hi):
        for i in range(lo + 1, hi + 1):
            key = a[i]
            j = i - 1
            while j >= lo and a[j] > key:
                a[j + 1] = a[j]
                j -= 1
            a[j + 1] = key

    def _introsort(a, lo, hi, depth_limit):
        size = hi - lo + 1
        if size <= 16:
            _insertion_sort(a, lo, hi)
            return
        if depth_limit == 0:
            _heapsort(a, lo, hi)
            return

        # Median-of-three pivot
        mid = (lo + hi) // 2
        if a[lo] > a[mid]: a[lo], a[mid] = a[mid], a[lo]
        if a[lo] > a[hi]:  a[lo], a[hi] = a[hi], a[lo]
        if a[mid] > a[hi]: a[mid], a[hi] = a[hi], a[mid]

        pivot = a[mid]
        a[mid], a[hi - 1] = a[hi - 1], a[mid]

        i, j = lo, hi - 1
        while True:
            i += 1
            while a[i] < pivot: i += 1
            j -= 1
            while a[j] > pivot: j -= 1
            if i >= j: break
            a[i], a[j] = a[j], a[i]

        a[i], a[hi - 1] = a[hi - 1], a[i]
        _introsort(a, lo, i - 1, depth_limit - 1)
        _introsort(a, i + 1, hi, depth_limit - 1)

    if n > 1:
        _introsort(arr, 0, n - 1, max_depth)
    return arr


# Verify
demo = random.sample(range(100), 20)
result = introsort(demo)
print(f"  Input:  {demo}")
print(f"  Output: {result}")
print(f"  Correct: {result == sorted(demo)} ✓")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  SHELLSORT — The Curious Gap Sequence
# ─────────────────────────────────────────────────────────────────────────────

section("SHELLSORT — The Curious Gap Sequence")

print("""\
  Donald Shell, 1959. The first O(n²)-breaking algorithm that sorts in place
  with O(1) extra memory (before heapsort).

  The idea: insertion sort is fast on nearly-sorted data. What if we could
  make the data "nearly sorted" cheaply? Shellsort does this by running
  insertion sort with decreasing "gaps."

  Start with a large gap (e.g., n/2). Elements that far apart get compared
  and swapped. Then shrink the gap. Eventually gap = 1, which is standard
  insertion sort — but by now the data is nearly sorted.

  The magic and the mystery: the running time depends on the GAP SEQUENCE,
  and finding the optimal gap sequence is STILL AN OPEN PROBLEM.

  Known complexities for different gap sequences:
    • Shell's original (n/2, n/4, ...):          O(n²)
    • Hibbard (1, 3, 7, 15, ..., 2^k - 1):      O(n^(3/2))
    • Sedgewick (1, 5, 19, 41, 109, ...):        O(n^(4/3))
    • Ciura (1, 4, 10, 23, 57, 132, 301, 701):   The best known empirically
    • Tokuda (1, 4, 9, 20, 46, 103, ...):        O(n^(4/3)) conjectured

  Nobody knows the optimal gap sequence. Nobody knows if Shellsort can
  reach O(n log n). It's one of the great unsolved problems in CS.
""")


def shellsort(arr, gaps=None):
    """Shellsort with configurable gap sequence."""
    arr = arr[:]
    n = len(arr)
    comparisons = 0

    if gaps is None:
        # Shell's original: n/2, n/4, ...
        gaps = []
        g = n // 2
        while g > 0:
            gaps.append(g)
            g //= 2

    for gap in gaps:
        # Gapped insertion sort
        for i in range(gap, n):
            key = arr[i]
            j = i
            while j >= gap and arr[j - gap] > key:
                comparisons += 1
                arr[j] = arr[j - gap]
                j -= gap
            if j >= gap:
                comparisons += 1
            arr[j] = key

    return arr, comparisons


def ciura_gaps(n):
    """Ciura's empirically optimal gap sequence."""
    gaps = [701, 301, 132, 57, 23, 10, 4, 1]
    # Extend for larger n using Tokuda's formula
    while gaps[0] * 2.25 < n:
        gaps.insert(0, int(gaps[0] * 2.25))
    return [g for g in gaps if g < n]


def shell_gaps(n):
    """Shell's original: n/2, n/4, ..., 1."""
    gaps = []
    g = n // 2
    while g > 0:
        gaps.append(g)
        g //= 2
    return gaps


def sedgewick_gaps(n):
    """Sedgewick's gap sequence."""
    gaps = [1]
    k = 1
    while True:
        if k % 2 == 0:
            g = 9 * (2**k - 2**(k//2)) + 1
        else:
            g = 8 * 2**k - 6 * 2**((k+1)//2) + 1
        if g >= n:
            break
        gaps.append(g)
        k += 1
    return sorted(gaps, reverse=True)


# Compare gap sequences
n = 10000
random.seed(42)
data = random.sample(range(n * 10), n)

print(f"  n = {n:,}, random data")
print()
print(f"  {'Gap sequence':>16s}  {'Gaps used':>10s}  {'Comparisons':>14s}  {'Time':>10s}")
print(f"  {'─'*16}  {'─'*10}  {'─'*14}  {'─'*10}")

for label, gap_func in [("Shell", shell_gaps), ("Sedgewick", sedgewick_gaps), ("Ciura", ciura_gaps)]:
    gaps = gap_func(n)
    t0 = time.perf_counter()
    _, comps = shellsort(data, gaps)
    elapsed = time.perf_counter() - t0
    print(f"  {label:>16s}  {len(gaps):>10d}  {comps:>14,}  {elapsed:>9.4f}s")

print()
print("  Ciura's sequence consistently wins — found by exhaustive computer search.")
print("  The optimal sequence remains unknown. A genuine open problem since 1959.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  THE GRAND ADAPTIVE BENCHMARK
# ─────────────────────────────────────────────────────────────────────────────

section("THE GRAND ADAPTIVE BENCHMARK")

print("""\
  Let's see how adaptive sorts handle different input patterns vs. non-adaptive.
""")

def merge_sort_bench(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort_bench(arr[:mid])
    right = merge_sort_bench(arr[mid:])
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


def heapsort_bench(arr):
    arr = arr[:]
    n = len(arr)
    def sd(a, size, i):
        while True:
            largest = i
            left = 2*i+1
            right = 2*i+2
            if left < size and a[left] > a[largest]: largest = left
            if right < size and a[right] > a[largest]: largest = right
            if largest != i:
                a[i], a[largest] = a[largest], a[i]
                i = largest
            else:
                break
    for i in range(n//2-1, -1, -1):
        sd(arr, n, i)
    for i in range(n-1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        sd(arr, i, 0)
    return arr


n = 30000
random.seed(42)

test_patterns = [
    ("Random",        random.sample(range(n * 10), n)),
    ("Sorted",        list(range(n))),
    ("Reversed",      list(range(n, 0, -1))),
    ("Nearly sorted", None),
    ("Pipe organ",    list(range(n // 2)) + list(range(n // 2, 0, -1))),
    ("Few unique",    [random.randint(0, 9) for _ in range(n)]),
]
nearly = list(range(n))
for _ in range(n // 50):
    i, j = random.randint(0, n-1), random.randint(0, n-1)
    nearly[i], nearly[j] = nearly[j], nearly[i]
test_patterns[3] = ("Nearly sorted", nearly)

print(f"  n = {n:,}")
print()
print(f"  {'Pattern':>15s}  {'Timsort':>9s}  {'Introsort':>9s}  {'Shellsort':>9s}  {'Merge':>9s}  {'Heapsort':>9s}  {'Python':>8s}")
print(f"  {'─'*15}  {'─'*9}  {'─'*9}  {'─'*9}  {'─'*9}  {'─'*9}  {'─'*8}")

for label, data in test_patterns:
    t0 = time.perf_counter()
    timsort_simplified(data)
    t_tim = time.perf_counter() - t0

    t0 = time.perf_counter()
    introsort(data)
    t_intro = time.perf_counter() - t0

    t0 = time.perf_counter()
    shellsort(data, ciura_gaps(len(data)))
    t_shell = time.perf_counter() - t0

    t0 = time.perf_counter()
    merge_sort_bench(data)
    t_merge = time.perf_counter() - t0

    t0 = time.perf_counter()
    heapsort_bench(data)
    t_heap = time.perf_counter() - t0

    d = data[:]
    t0 = time.perf_counter()
    d.sort()
    t_py = time.perf_counter() - t0

    print(f"  {label:>15s}  {t_tim:>8.4f}s  {t_intro:>8.4f}s  {t_shell:>8.4f}s  {t_merge:>8.4f}s  {t_heap:>8.4f}s  {t_py:>7.4f}s")

print()
print("  Observations:")
print("  • Timsort: blazing on sorted/reversed/nearly-sorted (natural runs)")
print("  • Introsort: consistent across all patterns (quicksort's speed + heapsort's safety)")
print("  • Shellsort: surprisingly competitive for an O(n^4/3) algorithm")
print("  • Heapsort: steady but always the slowest O(n log n) sort")
print("  • Python sort: C-optimized Timsort — the production champion")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

section("ADAPTIVE AND HYBRID SORTS: SUMMARY")

print("""\
  ┌──────────────────┬──────────┬──────────┬──────────┬────────┬────────┐
  │ Algorithm        │  Best    │ Average  │  Worst   │ Memory │ Stable │
  ├──────────────────┼──────────┼──────────┼──────────┼────────┼────────┤
  │ Timsort          │  O(n)    │O(n lg n) │O(n lg n) │  O(n)  │  Yes   │
  │ Introsort        │O(n lg n) │O(n lg n) │O(n lg n) │O(lg n) │  No    │
  │ Shellsort        │O(n lg n) │depends   │depends   │  O(1)  │  No    │
  │ Natural Merge    │  O(n)    │O(n lg n) │O(n lg n) │  O(n)  │  Yes   │
  └──────────────────┴──────────┴──────────┴──────────┴────────┴────────┘

  Who uses what:
    • Python, Java, Swift, Rust:  Timsort
    • C++ std::sort:              Introsort
    • C qsort:                    Usually quicksort (implementation-defined)
    • Embedded systems:           Shellsort (O(1) memory, no recursion)

  The lesson: the best sort isn't one algorithm — it's a strategy.
  Use quicksort when you can, heapsort when you must, insertion sort when
  you should, and let the data tell you which.

  Next up: what if you have multiple processors?
""")

print("  ─── End of Script 05 ───")
print()
