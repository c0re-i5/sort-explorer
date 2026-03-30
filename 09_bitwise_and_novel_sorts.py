#!/usr/bin/env python3
"""
09_bitwise_and_novel_sorts.py — Bitwise Alchemy: When Binary Meets Order

What happens when you take the binary tricks from [← repo 4: bit-tricks],
the positional encoding from [← repo 3: number-systems], the signal
decomposition from [← repo 5: waveguides], the Newton-style estimation
from [← repo 6: fisr-to-conway], and the graph intuition from [← repo 2:
navigational-pathfinding] — and point them all at sorting?

You get algorithms that nobody teaches in textbooks. Algorithms where bits
ARE the comparisons, where gravity is computed with popcount, where sorted
position is estimated then refined like Newton's method, where wavelet trees
decompose order like Fourier decomposes signal, where cellular automata
evolve disorder into order, and where bit-interleaving turns multi-key
sorting into a single-pass scan.

These are not toys (well, most aren't). Several are used in real systems —
databases, spatial indexing, GPU programming. Others are genuinely new
combinations of ideas from across this series.

Topics: binary radix exchange · bit-parallel gravity · Newton's estimate sort ·
wavelet tree sort · cellular automaton sort · Z-order (Morton) sort ·
cross-repo synthesis · when bits think for you
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


def is_sorted(arr):
    return all(arr[i] <= arr[i+1] for i in range(len(arr) - 1))


def show_array_bars(arr, width=40, label=""):
    """ASCII bar visualization."""
    mx = max(arr) if arr else 1
    if label:
        print(f"  {label}")
    for val in arr:
        bar_len = int(val / mx * width)
        print(f"  {val:>4d} │{'█' * bar_len}")
    print()


def show_bits(val, bits=8):
    """Show a value as a binary string."""
    return format(val, f'0{bits}b')


def popcount(x):
    """Count the number of 1-bits. [← repo 4: bit-tricks]"""
    count = 0
    while x:
        count += 1
        x &= x - 1  # Brian Kernighan's trick
    return count


# ─────────────────────────────────────────────────────────────────────────────
#  INTRODUCTION — WHEN BITS DO THE SORTING
# ─────────────────────────────────────────────────────────────────────────────

section("WHEN BITS DO THE SORTING")

print("""\
  Script 04 showed us that non-comparison sorts bypass the n·log·n barrier
  by using the VALUES of elements directly. Script 06 showed us that
  parallelism can sort in O(log²n) depth. Script 04 in repo 4 (bit-tricks)
  showed us that individual bits carry enormous information.

  This script asks: what if we combine all three ideas?

  Instead of comparing elements, we'll INSPECT THEIR BITS.
  Instead of shuffling whole values, we'll use BIT PARALLELISM.
  Instead of sorting blindly, we'll ESTIMATE positions, then refine.
  Instead of treating data as numbers, we'll DECOMPOSE it like a signal.
  Instead of a top-down algorithm, we'll let LOCAL RULES evolve order.

  Six algorithms. Six ideas stolen from across this repository series.
  Let's begin.
""")


# ─────────────────────────────────────────────────────────────────────────────
#  1. RADIX EXCHANGE SORT — Binary Quicksort
#     The missing bridge between quicksort and radix sort
#     [← repo 4: bit-tricks, repo 3: number-systems]
# ─────────────────────────────────────────────────────────────────────────────

section("1. RADIX EXCHANGE SORT — Binary Quicksort")

print("""\
  Quicksort picks a pivot and partitions around it. Radix sort processes
  digits. What if we combined them?

  Radix exchange sort (also called binary quicksort, or bitwise quicksort)
  partitions on individual bits, from the most significant bit downward.
  Elements with a 0 in the current bit go left; elements with a 1 go right.
  Then recurse on each half with the next bit.

  No pivot selection. No value comparisons. Just bit inspection.

  ┌──────────────────────────────────────────────────────────────────┐
  │  It's quicksort's partitioning logic + radix sort's digit idea  │
  │  = a hybrid that needs zero comparisons                         │
  └──────────────────────────────────────────────────────────────────┘

  How it works on [6, 2, 7, 3, 5, 1, 4, 0] (3-bit numbers):

    Bit 2 (MSB):  6=110  2=010  7=111  3=011  5=101  1=001  4=100  0=000
                   ─1──   ─0──   ─1──   ─0──   ─1──   ─0──   ─1──   ─0──
    Partition:     [2, 3, 1, 0]  |  [6, 7, 5, 4]

    Bit 1 (left):  2=010  3=011  1=001  0=000
                    ─1──   ─1──   ─0──   ─0──
    Partition:      [1, 0]  |  [2, 3]

    Bit 0 (left-left):  1=001  0=000
                         ──1─   ──0─
    Partition:           [0]  |  [1]

    ...and so on for each sub-partition.
    Result: [0, 1, 2, 3, 4, 5, 6, 7]

  Complexity: O(b·n) where b = number of bits. For 32-bit ints: O(32n).
  Space: O(b) stack depth (in-place partitioning like quicksort).
  Unlike quicksort, there's no bad pivot — the bits ARE the partitioner.
""")


def radix_exchange_sort(arr):
    """Radix exchange sort: binary quicksort using bit inspection."""
    if not arr:
        return []
    arr = arr[:]
    max_val = max(arr)
    if max_val == 0:
        return arr
    max_bit = max_val.bit_length() - 1

    def _sort(lo, hi, bit):
        if lo >= hi or bit < 0:
            return

        # Partition: 0-bits go left, 1-bits go right
        i, j = lo, hi
        while i <= j:
            while i <= j and not (arr[i] >> bit & 1):
                i += 1
            while i <= j and (arr[j] >> bit & 1):
                j -= 1
            if i < j:
                arr[i], arr[j] = arr[j], arr[i]
                i += 1
                j -= 1

        # j is last 0-bit element, i is first 1-bit element
        _sort(lo, j, bit - 1)
        _sort(i, hi, bit - 1)

    _sort(0, len(arr) - 1, max_bit)
    return arr


def radix_exchange_sort_traced(arr):
    """Traced version showing bit-level partitioning."""
    if not arr:
        return [], []
    arr = arr[:]
    max_val = max(arr)
    if max_val == 0:
        return arr, []
    max_bit = max_val.bit_length() - 1
    trace = []

    def _sort(lo, hi, bit, depth=0):
        if lo >= hi or bit < 0:
            return

        indent = "    " + "  " * depth
        before = arr[lo:hi+1]
        trace.append(f"{indent}Bit {bit}: {before}")

        i, j = lo, hi
        while i <= j:
            while i <= j and not (arr[i] >> bit & 1):
                i += 1
            while i <= j and (arr[j] >> bit & 1):
                j -= 1
            if i < j:
                arr[i], arr[j] = arr[j], arr[i]
                i += 1
                j -= 1

        left_part = arr[lo:j+1] if j >= lo else []
        right_part = arr[i:hi+1] if i <= hi else []
        trace.append(f"{indent}  → 0s:{left_part}  1s:{right_part}")

        _sort(lo, j, bit - 1, depth + 1)
        _sort(i, hi, bit - 1, depth + 1)

    _sort(0, len(arr) - 1, max_bit)
    return arr, trace


# Demonstration
demo = [6, 2, 7, 3, 5, 1, 4, 0]
print(f"  Input: {demo}")
bits = max(demo).bit_length()
print(f"  Binary: {[show_bits(x, bits) for x in demo]}")
print()

result, trace = radix_exchange_sort_traced(demo)
print("  Trace:")
for line in trace:
    print(line)
print()
print(f"  Output: {result}")
print(f"  Correct: {result == sorted(demo)} ✓")
print()

subsection("No Comparisons, No Problem")

print("""\
  Notice what we DIDN'T do: we never asked "is A < B?"

  Every decision was "is bit k of this element 0 or 1?" — a single AND
  and a branch. No comparisons between elements at all.

  This means radix exchange sort is immune to comparison-sort adversarial
  inputs. There's no "sorted input" worst case, no "all-equal" degenerate
  case. The work is always O(b·n), determined by the bit-width, not the
  data distribution.

  ┌────────────────────┬────────────┬───────────┬──────────┬────────┐
  │ Algorithm          │ Best       │ Average   │ Worst    │ Stable │
  ├────────────────────┼────────────┼───────────┼──────────┼────────┤
  │ Quicksort          │ O(n log n) │ O(n log n)│ O(n²)    │ No     │
  │ Radix Exchange     │ O(b·n)     │ O(b·n)    │ O(b·n)   │ No     │
  │ LSD Radix Sort     │ O(d(n+b))  │ O(d(n+b)) │ O(d(n+b))│ Yes    │
  └────────────────────┴────────────┴───────────┴──────────┴────────┘
""")

# Benchmark: radix exchange vs quicksort vs LSD radix
print("  Benchmark: Radix Exchange vs. Quicksort vs. Python sorted()")
print("  ────────────────────────────────────────────────────────────")


def quicksort_hoare(arr):
    arr = arr[:]
    def _sort(lo, hi):
        if lo >= hi:
            return
        pivot = arr[(lo + hi) // 2]
        i, j = lo, hi
        while i <= j:
            while arr[i] < pivot: i += 1
            while arr[j] > pivot: j -= 1
            if i <= j:
                arr[i], arr[j] = arr[j], arr[i]
                i += 1
                j -= 1
        _sort(lo, j)
        _sort(i, hi)
    if len(arr) > 1:
        _sort(0, len(arr) - 1)
    return arr


for n in [1000, 10_000, 100_000]:
    data = [random.randint(0, n * 10) for _ in range(n)]

    t0 = time.perf_counter()
    r1 = radix_exchange_sort(data)
    t_rex = time.perf_counter() - t0

    t0 = time.perf_counter()
    r2 = quicksort_hoare(data)
    t_qs = time.perf_counter() - t0

    t0 = time.perf_counter()
    r3 = sorted(data)
    t_py = time.perf_counter() - t0

    assert r1 == r3 and r2 == r3
    print(f"  n={n:>7,}: RadixExch={t_rex:.4f}s  Quicksort={t_qs:.4f}s  Python={t_py:.4f}s")

print()


# ─────────────────────────────────────────────────────────────────────────────
#  2. BIT-PARALLEL GRAVITY SORT — Bead Sort with Real Bits
#     [← repo 4: bit-tricks (popcount, bit packing)]
# ─────────────────────────────────────────────────────────────────────────────

section("2. BIT-PARALLEL GRAVITY SORT — Bead Sort with Real Bits")

print("""\
  Script 07 implemented bead/gravity sort as a 2D grid simulation: beads
  on an abacus fall under gravity. It's O(n·max_val) with a big grid.

  But what if each column of the abacus is a SINGLE INTEGER? Each bead
  is a bit. Gravity = counting 1-bits (popcount) and packing them to
  the bottom.

  This is bit-parallel gravity sort. Instead of iterating over an n×m
  grid cell by cell, we pack each column into a machine word and let
  bit operations do the work.

  Physical model:
    Column 0:  1 1 0 1 1 → popcount = 4 → pack to bottom: 0 1 1 1 1
    Column 1:  1 0 1 1 0 → popcount = 3 → pack to bottom: 0 0 1 1 1
    Column 2:  1 1 1 0 0 → popcount = 3 → pack to bottom: 0 0 1 1 1

  Each column-drop is a single popcount + bit-shift. No loops over rows.

  [← repo 4: bit-tricks] — popcount (Brian Kernighan's trick), bit packing,
  the idea that a single integer can represent an entire column of data.
""")


def gravity_sort_naive(arr):
    """Classic bead sort: O(n × max_val) grid simulation."""
    if not arr:
        return []
    max_val = max(arr)
    if max_val == 0:
        return arr[:]
    n = len(arr)

    # Build grid: grid[row][col] = 1 if bead present
    grid = [[0] * max_val for _ in range(n)]
    for i, val in enumerate(arr):
        for j in range(val):
            grid[i][j] = 1

    # Gravity: count beads in each column, pack to bottom
    result_grid = [[0] * max_val for _ in range(n)]
    for col in range(max_val):
        bead_count = sum(grid[row][col] for row in range(n))
        for row in range(n - bead_count, n):
            result_grid[row][col] = 1

    return [sum(result_grid[row]) for row in range(n)]


def gravity_sort_bitparallel(arr):
    """Bit-parallel gravity sort: columns packed into integers.

    Each column is a single integer where bit i = 1 means row i has a bead.
    Gravity = popcount to count beads, then create a mask with that many
    lowest bits set (packed to the bottom rows).
    """
    if not arr:
        return []
    max_val = max(arr)
    if max_val == 0:
        return arr[:]
    n = len(arr)

    # Pack columns into integers: column[j] has bit i set if arr[i] >= j+1
    columns = [0] * max_val
    for i, val in enumerate(arr):
        for j in range(val):
            columns[j] |= (1 << i)

    # Gravity: count bits, pack to bottom (highest row indices)
    for j in range(max_val):
        count = popcount(columns[j])
        # Set the bottom 'count' rows: bits (n-count) through (n-1)
        columns[j] = ((1 << count) - 1) << (n - count)

    # Read back: value of row i = number of columns where bit i is set
    result = [0] * n
    for j in range(max_val):
        col = columns[j]
        for i in range(n):
            if col & (1 << i):
                result[i] += 1

    return result


# Visualize the process
demo = [3, 1, 4, 1, 5, 2]
max_v = max(demo)
n = len(demo)
print(f"  Input: {demo}")
print()

print("  Bead grid (rows = elements, columns = unary value):")
for i, val in enumerate(demo):
    beads = "●" * val + "○" * (max_v - val)
    print(f"    [{val}]  {beads}")

print()
print("  Columns as integers (bit i = row i has bead):")
columns = [0] * max_v
for i, val in enumerate(demo):
    for j in range(val):
        columns[j] |= (1 << i)
for j in range(max_v):
    bits = show_bits(columns[j], n)
    print(f"    Col {j}: {bits}  (popcount = {popcount(columns[j])})")

print()
print("  After gravity (popcount → pack to bottom):")
for j in range(max_v):
    count = popcount(columns[j])
    fallen = ((1 << count) - 1) << (n - count)
    bits = show_bits(fallen, n)
    print(f"    Col {j}: {bits}  ({count} beads → bottom)")

print()
result = gravity_sort_bitparallel(demo)
print(f"  Output: {result}")
print(f"  Correct: {result == sorted(demo)} ✓")
print()

subsection("Bit-Parallel vs. Naive: The Speedup")

print("""\
  The naive version does n × max_val individual cell operations.
  The bit-parallel version does max_val popcount operations for gravity,
  then n × max_val bit-tests for readback. The gravity step itself is
  O(max_val) instead of O(n × max_val).

  On modern hardware, popcount is a SINGLE INSTRUCTION (POPCNT on x86).
  Even in Python, the bit-manipulation version packs multiple "rows" into
  one integer operation — a form of SIMD within a register (SWAR).

  [← repo 4: bit-tricks] — SWAR is the technique of treating a wide
  integer as multiple narrow lanes. Here, each bit-lane is a "row" of
  our sorting grid.

  Complexity:
    Naive bead sort:       O(n × max_val) time, O(n × max_val) space
    Bit-parallel gravity:  O(n × max_val) time*, O(max_val) space
    *But with machine-word parallelism hidden in the constants.

  Constraint: only works on non-negative integers (like all bead sorts).
""")

print("  Benchmark: Naive vs. Bit-Parallel Gravity Sort")
print("  ──────────────────────────────────────────────")

for n_size in [200, 500, 1000]:
    data = [random.randint(0, 100) for _ in range(n_size)]

    t0 = time.perf_counter()
    r1 = gravity_sort_naive(data)
    t_naive = time.perf_counter() - t0

    t0 = time.perf_counter()
    r2 = gravity_sort_bitparallel(data)
    t_bit = time.perf_counter() - t0

    assert r1 == sorted(data) and r2 == sorted(data)
    speedup = t_naive / t_bit if t_bit > 0 else float('inf')
    print(f"  n={n_size:>5}, max=100:  Naive={t_naive:.4f}s  BitParallel={t_bit:.4f}s  ({speedup:.1f}× speedup)")

print()


# ─────────────────────────────────────────────────────────────────────────────
#  3. NEWTON'S ESTIMATE SORT — Guess, Place, Refine
#     [← repo 6: fisr-to-conway-and-beyond (Newton's method, FISR)]
# ─────────────────────────────────────────────────────────────────────────────

section("3. NEWTON'S ESTIMATE SORT — Guess, Place, Refine")

print("""\
  The Fast Inverse Square Root (FISR) algorithm [← repo 6] had a beautiful
  philosophy: make a rough estimate using bit tricks, then refine with
  Newton's method. One iteration of refinement was enough.

  What if we applied the same philosophy to sorting?

  Step 1 — THE ESTIMATE (the "magic guess"):
    For each element, estimate its final sorted position:
      estimated_pos = floor((value - min) / (max - min) × (n - 1))
    This assumes roughly uniform distribution. If the data IS uniform,
    every element lands in exactly the right spot. Done in O(n).

  Step 2 — PLACEMENT (the "initial shove"):
    Place each element at its estimated position. When collisions occur
    (two elements estimate the same position), chain them in a bucket.

  Step 3 — THE REFINEMENT (Newton's "polish"):
    Each bucket is small (if the estimate was good). Sort each bucket
    with insertion sort — which is O(n) on small/nearly-sorted data.

  This is essentially bucket sort with a Newton's-method-inspired framing:
  the estimate function is the "initial guess" and the local insertion sort
  is the "refinement iteration."

  What makes it novel is the ADAPTIVE refinement. If the initial estimate
  places elements perfectly, we do zero refinement. If it's slightly off,
  we do minimal work. The worse the estimate, the more refinement — just
  like Newton's method converging from a bad initial guess.
""")


def newtons_estimate_sort(arr):
    """Newton's Estimate Sort: guess positions, then refine.

    Like FISR: one good estimate + one refinement pass.
    """
    if len(arr) <= 1:
        return arr[:]
    arr_copy = arr[:]
    n = len(arr_copy)
    min_val = min(arr_copy)
    max_val = max(arr_copy)

    if min_val == max_val:
        return arr_copy  # all equal

    # Step 1: Estimate positions and distribute into buckets
    buckets = [[] for _ in range(n)]
    for val in arr_copy:
        # The "magic guess": linear interpolation
        pos = int((val - min_val) / (max_val - min_val) * (n - 1))
        buckets[pos].append(val)

    # Step 2: Refine each bucket with insertion sort (the "Newton iteration")
    result = []
    total_refinement_work = 0
    for bucket in buckets:
        # Insertion sort on the bucket — O(k²) but k is tiny if estimate is good
        for i in range(1, len(bucket)):
            key = bucket[i]
            j = i - 1
            while j >= 0 and bucket[j] > key:
                bucket[j + 1] = bucket[j]
                j -= 1
                total_refinement_work += 1
            bucket[j + 1] = key
        result.extend(bucket)

    return result


def newtons_estimate_sort_traced(arr):
    """Traced version showing estimate accuracy."""
    if len(arr) <= 1:
        return arr[:], 0, 0
    n = len(arr)
    min_val = min(arr)
    max_val = max(arr)

    if min_val == max_val:
        return arr[:], 0, 0

    buckets = [[] for _ in range(n)]
    estimates = []
    for val in arr:
        pos = int((val - min_val) / (max_val - min_val) * (n - 1))
        buckets[pos].append(val)
        estimates.append(pos)

    perfect_placements = sum(1 for b in buckets if len(b) == 1)
    refinement_work = 0
    result = []
    for bucket in buckets:
        for i in range(1, len(bucket)):
            key = bucket[i]
            j = i - 1
            while j >= 0 and bucket[j] > key:
                bucket[j + 1] = bucket[j]
                j -= 1
                refinement_work += 1
            bucket[j + 1] = key
        result.extend(bucket)

    return result, perfect_placements, refinement_work


# Demo with uniform data (best case for the estimate)
random.seed(42)
demo = [random.randint(0, 99) for _ in range(20)]
print(f"  Input (uniform random): {demo}")

result, perfect, work = newtons_estimate_sort_traced(demo)
print(f"  Output: {result}")
print(f"  Correct: {result == sorted(demo)} ✓")
print(f"  Perfect placements: {perfect}/{len(demo)} ({100*perfect//len(demo)}% accuracy)")
print(f"  Refinement work (swaps): {work}")
print()

# Demo with skewed data (stress test for the estimate)
demo_skewed = [int(x**2) for x in range(20)]  # quadratic distribution
random.shuffle(demo_skewed)
print(f"  Input (quadratic distribution): {demo_skewed}")

result, perfect, work = newtons_estimate_sort_traced(demo_skewed)
print(f"  Output: {result}")
print(f"  Correct: {result == sorted(demo_skewed)} ✓")
print(f"  Perfect placements: {perfect}/{len(demo_skewed)} ({100*perfect//len(demo_skewed)}% accuracy)")
print(f"  Refinement work (swaps): {work}")
print()

subsection("The FISR Parallel: Estimate Quality vs. Refinement Cost")

print("""\
  ┌────────────────────────┬────────────────────────────────────────┐
  │ FISR                   │ Newton's Estimate Sort                │
  ├────────────────────────┼────────────────────────────────────────┤
  │ Bit-hack initial guess │ Linear interpolation initial guess    │
  │ 1-2 Newton iterations  │ Insertion sort refinement per bucket  │
  │ Better guess → faster  │ Better estimate → fewer swaps         │
  │ Works on floats        │ Works on any comparable elements      │
  └────────────────────────┴────────────────────────────────────────┘

  Complexity:
    Best case (uniform data):  O(n)      — every element goes to its bucket
    Average case:              O(n + k²) — k = avg bucket size ≈ constant
    Worst case (adversarial):  O(n²)     — all elements in one bucket

  The irony: this IS bucket sort. But the framing reveals something deeper
  — the quality of your initial estimate determines the total work, just
  like Newton's method. And the "magic number" in FISR is just a very good
  initial estimate for 1/√x. Here, linear interpolation is our magic number.
""")

print("  Benchmark across distributions:")
print("  ───────────────────────────────")

for label, gen in [
    ("Uniform [0,n)",    lambda n: [random.randint(0, n - 1) for _ in range(n)]),
    ("Normal (μ=500)",   lambda n: [max(0, int(random.gauss(500, 100))) for _ in range(n)]),
    ("Exponential",      lambda n: [int(random.expovariate(0.01)) for _ in range(n)]),
    ("Squared",          lambda n: [random.randint(0, n)**2 for _ in range(n)]),
]:
    n = 50_000
    data = gen(n)
    t0 = time.perf_counter()
    r = newtons_estimate_sort(data)
    t_est = time.perf_counter() - t0

    t0 = time.perf_counter()
    r2 = sorted(data)
    t_py = time.perf_counter() - t0

    assert r == r2
    ratio = t_est / t_py if t_py > 0 else float('inf')
    print(f"  {label:<20s}: Newton={t_est:.4f}s  Python={t_py:.4f}s  (ratio: {ratio:.1f}×)")

print()


# ─────────────────────────────────────────────────────────────────────────────
#  4. WAVELET TREE SORT — Signal Decomposition Meets Ordering
#     [← repo 5: waveguides (signal decomposition, frequency analysis)]
# ─────────────────────────────────────────────────────────────────────────────

section("4. WAVELET TREE SORT — Signal Decomposition Meets Ordering")

print("""\
  A wavelet tree decomposes a sequence by splitting its alphabet at the
  median, recursively. At each level, elements below the median go left
  (encoded as 0), elements at or above go right (encoded as 1). The bit
  vectors at each level capture the "frequency structure" of the sequence.

  This is the same idea as signal decomposition [← repo 5: waveguides] —
  split a signal into low-frequency (left) and high-frequency (right)
  components, recursively. In wavelet trees, "frequency" is value rank.

  To SORT using a wavelet tree:
    1. Build the tree: at each node, partition elements around the median
       of their current sub-alphabet. Record a bit vector (0=left, 1=right).
    2. Read the leaves left-to-right: they're in sorted order.

  The tree has depth ⌈log₂(σ)⌉ where σ = alphabet size (distinct values).
  Each level processes all n elements once. Total: O(n log σ).

  Used in practice for:
    • Compressed full-text indices (FM-index, etc.)
    • Rank/select queries on sequences
    • Range quantile queries (find the k-th smallest in a range)
""")


def wavelet_tree_sort(arr):
    """Sort by building a wavelet tree and reading leaves left-to-right.

    At each level, partition around the median of the current alphabet.
    The leaves, read left-to-right, give the sorted order.
    """
    if len(arr) <= 1:
        return arr[:]

    def _build_and_collect(elements, lo_val, hi_val):
        """Recursively split by median of value range, collect sorted at leaves."""
        if not elements:
            return []
        if lo_val >= hi_val:
            return list(elements)  # all same value — leaf node

        # Split point: median of the value range
        mid_val = (lo_val + hi_val) // 2

        # Partition: values <= mid go left (bit 0), values > mid go right (bit 1)
        left = []
        right = []
        for val in elements:
            if val <= mid_val:
                left.append(val)
            else:
                right.append(val)

        # Recurse and concatenate (left leaves come before right leaves)
        return _build_and_collect(left, lo_val, mid_val) + \
               _build_and_collect(right, mid_val + 1, hi_val)

    min_val = min(arr)
    max_val = max(arr)
    return _build_and_collect(arr, min_val, max_val)


def wavelet_tree_sort_traced(arr):
    """Traced version showing the decomposition tree."""
    if len(arr) <= 1:
        return arr[:], []
    trace = []

    def _build(elements, lo_val, hi_val, depth=0):
        if not elements:
            return []
        if lo_val >= hi_val:
            return list(elements)

        mid_val = (lo_val + hi_val) // 2
        left = []
        right = []
        bitvec = []
        for val in elements:
            if val <= mid_val:
                left.append(val)
                bitvec.append(0)
            else:
                right.append(val)
                bitvec.append(1)

        indent = "    " + "  " * depth
        trace.append(
            f"{indent}Split [{lo_val}..{hi_val}] at {mid_val}: "
            f"{''.join(map(str, bitvec))} → L:{left} R:{right}"
        )

        return _build(left, lo_val, mid_val, depth + 1) + \
               _build(right, mid_val + 1, hi_val, depth + 1)

    result = _build(arr, min(arr), max(arr))
    return result, trace


# Demo
demo = [5, 2, 8, 1, 7, 3, 6, 4]
print(f"  Input: {demo}")
print(f"  Value range: [{min(demo)}..{max(demo)}]")
print()

result, trace = wavelet_tree_sort_traced(demo)
print("  Wavelet decomposition:")
for line in trace:
    print(line)
print()
print(f"  Leaves (left-to-right): {result}")
print(f"  Correct: {result == sorted(demo)} ✓")
print()

subsection("The Signal Processing Analogy")

print("""\
  Think of the input array as a signal. The wavelet tree is a transform:

  ┌──────────────────────┬──────────────────────────────────────────┐
  │ Signal Processing    │ Wavelet Tree Sort                        │
  ├──────────────────────┼──────────────────────────────────────────┤
  │ Input signal         │ Input array                              │
  │ Low/high frequencies │ Below/above median values                │
  │ Filter bank          │ Recursive median partitioning            │
  │ Wavelet coefficients │ Bit vectors at each level                │
  │ Reconstruction       │ Reading leaves = sorted output           │
  │ O(n log n) transform │ O(n log σ) sort                         │
  └──────────────────────┴──────────────────────────────────────────┘

  In repo 5 (waveguides), we saw that the DFT decomposes a time-domain
  signal into frequency components. Here, the wavelet tree decomposes a
  value-domain sequence into rank components. Same math, different domain.

  Complexity: O(n log σ) where σ = number of distinct values.
  When σ ≤ n: equivalent to or better than O(n log n).
  Space: O(n log σ) for the bit vectors (can be compressed in practice).
  Stable: Yes — equal elements preserve their relative order.
""")

# Benchmark
print("  Benchmark: Wavelet Tree Sort vs. Python sorted()")
print("  ────────────────────────────────────────────────")

for n in [5000, 20_000, 50_000]:
    data = [random.randint(0, 1000) for _ in range(n)]

    t0 = time.perf_counter()
    r1 = wavelet_tree_sort(data)
    t_wt = time.perf_counter() - t0

    t0 = time.perf_counter()
    r2 = sorted(data)
    t_py = time.perf_counter() - t0

    assert r1 == r2
    print(f"  n={n:>6,}, σ≤1000: Wavelet={t_wt:.4f}s  Python={t_py:.4f}s")

print()


# ─────────────────────────────────────────────────────────────────────────────
#  5. CELLULAR AUTOMATON SORT — Local Rules, Global Order
#     [← repo 6: fisr-to-conway-and-beyond (cellular automata, Conway)]
# ─────────────────────────────────────────────────────────────────────────────

section("5. CELLULAR AUTOMATON SORT — Local Rules, Global Order")

print("""\
  Conway's Game of Life [← repo 6] showed us that simple local rules can
  produce complex global behavior. Cellular automata don't have a central
  controller — each cell looks only at its neighbors and applies a rule.

  Can local rules sort an array? Yes.

  Rule: Each cell (element) simultaneously compares with its neighbor.
  If the left neighbor is larger, swap them. Apply this rule to ALL
  adjacent pairs at once, alternating between even-indexed and odd-indexed
  pairs.

  This is odd-even transposition sort — essentially bubble sort, but with
  ALL non-overlapping pairs swapping simultaneously. It's the sorting
  equivalent of a 1D cellular automaton.

  Physical analogy: imagine each array position is a cell in a 1D CA.
  The "state" of each cell is its value. The transition rule is:
    • Even step: cells at positions (0,1), (2,3), (4,5), ... compare-swap
    • Odd step:  cells at positions (1,2), (3,4), (5,6), ... compare-swap

  After at most n steps (generations), the array is sorted. The CA has
  evolved from disorder to order.

  On a parallel machine with n processors, each step is O(1), total O(n).
  Sequentially, it's O(n²) — but the STRUCTURE is fundamentally parallel.
""")


def ca_sort(arr, trace=False):
    """Cellular automaton sort: odd-even transposition.

    Each generation applies local swap rules to all pairs simultaneously.
    """
    arr = arr[:]
    n = len(arr)
    generations = []

    for gen in range(n):
        swapped = False
        # Even phase: compare (0,1), (2,3), (4,5), ...
        for i in range(0, n - 1, 2):
            if arr[i] > arr[i + 1]:
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
                swapped = True
        # Odd phase: compare (1,2), (3,4), (5,6), ...
        for i in range(1, n - 1, 2):
            if arr[i] > arr[i + 1]:
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
                swapped = True

        if trace:
            generations.append(arr[:])

        if not swapped:
            break

    if trace:
        return arr, generations
    return arr


# Visualize the CA evolution
demo = [8, 3, 6, 1, 7, 2, 5, 4]
print(f"  Input: {demo}")
print()
print("  Cellular automaton evolution:")
print("  ─────────────────────────────")

result, gens = ca_sort(demo, trace=True)
print(f"  Gen 0 (initial): {demo}")
for i, state in enumerate(gens):
    marker = " ✓ SORTED" if is_sorted(state) else ""
    print(f"  Gen {i+1:>2}:          {state}{marker}")

print()
print(f"  Sorted in {len(gens)} generations (max possible: {len(demo)})")
print()

subsection("Extended CA: Skip Connections")

print("""\
  Basic CA sort only compares immediate neighbors (gap = 1). What if cells
  could also "see" farther — like Wolfram's extended-neighborhood automata?

  We can add Shellsort-style gaps: first compare pairs at distance h, then
  progressively shrink h to 1. This is a CA with varying neighborhood size.

  Think of it as a CA that starts with long-range communication and
  progressively becomes more local — like cooling a crystal (simulated
  annealing for free!).
""")


def ca_sort_extended(arr):
    """Extended CA sort with Shellsort-style skip connections.

    First resolve long-range disorder with large gaps (extended neighborhood),
    then clean up with adjacent swaps (basic neighborhood).
    """
    arr = arr[:]
    n = len(arr)

    # Ciura's gap sequence [← script 05] as "neighborhood radii"
    gaps = [gap for gap in [301, 132, 57, 23, 10, 4, 1] if gap < n]

    for gap in gaps:
        for gen in range(n):
            swapped = False
            # Even phase
            for i in range(0, n - gap, 2 * gap):
                if arr[i] > arr[i + gap]:
                    arr[i], arr[i + gap] = arr[i + gap], arr[i]
                    swapped = True
            # Odd phase
            for i in range(gap, n - gap, 2 * gap):
                if arr[i] > arr[i + gap]:
                    arr[i], arr[i + gap] = arr[i + gap], arr[i]
                    swapped = True
            if not swapped:
                break

    return arr


# Benchmark CA variants
print("  Benchmark: Basic CA vs. Extended CA vs. Python sorted()")
print("  ──────────────────────────────────────────────────────")

for n in [500, 1000, 2000]:
    data = [random.randint(0, n * 10) for _ in range(n)]

    t0 = time.perf_counter()
    r1 = ca_sort(data)
    t_basic = time.perf_counter() - t0

    t0 = time.perf_counter()
    r2 = ca_sort_extended(data)
    t_ext = time.perf_counter() - t0

    t0 = time.perf_counter()
    r3 = sorted(data)
    t_py = time.perf_counter() - t0

    assert r1 == r3 and r2 == r3
    print(f"  n={n:>5}: Basic CA={t_basic:.4f}s  Extended CA={t_ext:.4f}s  Python={t_py:.4f}s")

print()

subsection("The CA Perspective on Sorting")

print("""\
  What makes this interesting isn't efficiency — it's the PARADIGM.

  Most sorting algorithms are centralized: a single decision-maker
  partitions, merges, or selects. CA sort is decentralized: every cell
  makes its own decision based on local information. There's no global
  coordinator.

  This maps to real systems:
    • Network packet sorting (each router makes local decisions)
    • Self-organizing particle systems
    • Distributed consensus without a leader

  ┌───────────────────────┬──────────────────────────────────────────┐
  │ Conway's Game of Life │ CA Sort                                  │
  ├───────────────────────┼──────────────────────────────────────────┤
  │ Local birth/death     │ Local compare-swap                      │
  │ Emergent structures   │ Emergent sorted order                   │
  │ Grid topology         │ Linear topology                         │
  │ Chaotic behavior      │ Guaranteed convergence (n steps)        │
  │ Undecidable halting   │ Always halts (provably)                 │
  └───────────────────────┴──────────────────────────────────────────┘

  Complexity:
    Basic CA:     O(n²) sequential, O(n) parallel with n processors
    Extended CA:  Better constants; Shellsort-like gap shrinking
    Space: O(1) — purely in-place, no extra memory
    Stable: Yes (odd-even transposition preserves equal-element order)
""")


# ─────────────────────────────────────────────────────────────────────────────
#  6. Z-ORDER (MORTON) SORT — Bit Interleaving for Multi-Key Data
#     [← repo 4: bit-tricks (bit interleaving) + repo 3: number-systems]
# ─────────────────────────────────────────────────────────────────────────────

section("6. Z-ORDER (MORTON) SORT — Bit Interleaving for Multi-Key Data")

print("""\
  How do you sort points in 2D space? By x? By y? By x-then-y?
  None of these preserve spatial locality well.

  Morton order (Z-order) interleaves the bits of each coordinate to form
  a single key. Sorting by this key produces a space-filling Z-curve that
  preserves locality better than any single-axis sort.

  Example: Point (x=5, y=3)
    x = 5 = 101₂
    y = 3 = 011₂

  Interleave bits (x bits in even positions, y bits in odd positions):
    x: 1_0_1   →  1 . 0 . 1 .
    y: 0_1_1   →  . 0 . 1 . 1
    Morton:        1 0 0 1 1 1  = 39₁₀

  [← repo 4: bit-tricks] — bit interleaving is a fundamental operation
  we explored in the context of Hilbert curves and spatial hashing.
  [← repo 3: number-systems] — the interleaved representation is a new
  positional encoding where digit positions alternate between dimensions.

  Used in practice:
    • Database indexing (SQLite R*Trees, ClickHouse)
    • GPU memory layouts (texture coordinates)
    • Barnes-Hut n-body simulation (octree construction)
    • Geospatial hashing (geohash is Z-order on lat/lng)
""")


def interleave_bits(x, y):
    """Interleave bits of x and y into a Morton code.

    Uses the bit-spreading technique from [← repo 4: bit-tricks].
    x bits go into even positions, y bits into odd positions.
    """
    def spread(v):
        # Spread bits of v apart, inserting zeros between each bit
        # 16-bit version (handles values up to 65535)
        v &= 0x0000FFFF
        v = (v | (v << 8)) & 0x00FF00FF
        v = (v | (v << 4)) & 0x0F0F0F0F
        v = (v | (v << 2)) & 0x33333333
        v = (v | (v << 1)) & 0x55555555
        return v
    return spread(x) | (spread(y) << 1)


def morton_sort_2d(points):
    """Sort 2D points by Z-order (Morton code).

    Preserves spatial locality: nearby points in 2D tend to be
    nearby in the sorted order.
    """
    # Compute Morton code for each point, sort by it
    keyed = [(interleave_bits(x, y), (x, y)) for x, y in points]
    keyed.sort(key=lambda item: item[0])
    return [pt for _, pt in keyed]


def interleave_bits_3d(x, y, z):
    """Interleave bits of three coordinates for 3D Morton code."""
    def spread3(v):
        v &= 0x000003FF  # 10-bit values
        v = (v | (v << 16)) & 0x030000FF
        v = (v | (v <<  8)) & 0x0300F00F
        v = (v | (v <<  4)) & 0x030C30C3
        v = (v | (v <<  2)) & 0x09249249
        return v
    return spread3(x) | (spread3(y) << 1) | (spread3(z) << 2)


def morton_sort_3d(points):
    """Sort 3D points by Z-order (Morton code)."""
    keyed = [(interleave_bits_3d(x, y, z), (x, y, z)) for x, y, z in points]
    keyed.sort(key=lambda item: item[0])
    return [pt for _, pt in keyed]


# Demo: visualize the Z-curve on a 4x4 grid
print("  Z-order traversal of a 4×4 grid:")
print("  ──────────────────────────────────")
print()

grid_points = [(x, y) for y in range(4) for x in range(4)]
sorted_pts = morton_sort_2d(grid_points)

# Create a grid showing Morton order
grid = [[0]*4 for _ in range(4)]
for order, (x, y) in enumerate(sorted_pts):
    grid[3-y][x] = order  # y=0 at bottom

print("  y")
for row_idx, row in enumerate(grid):
    y_val = 3 - row_idx
    cells = "  ".join(f"{v:>2d}" for v in row)
    print(f"  {y_val} │ {cells}")
print("    └───────────────")
print("      0   1   2   3  x")
print()
print("  The Z-shaped curve: 0→1→2→3 then 4→5→6→7 then ...")
print("  Reading order traces a Z at each scale — hence the name.")
print()

# Show bit interleaving for specific points
print("  Bit interleaving in detail:")
print("  ───────────────────────────")
example_points = [(0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (3, 3)]
for x, y in example_points:
    morton = interleave_bits(x, y)
    xbits = show_bits(x, 4)
    ybits = show_bits(y, 4)
    mbits = show_bits(morton, 8)
    print(f"  ({x},{y}):  x={xbits}  y={ybits}  →  morton={mbits} ({morton})")

print()

subsection("Spatial Locality: Why Z-Order Wins")

print("""\
  Sorting by x-then-y puts (0,0) and (0,999) adjacent — they're far apart!
  Morton order keeps spatially close points close in the sorted sequence.

  Measure: for each consecutive pair in sorted order, compute the Euclidean
  distance. Lower average distance = better spatial locality.
""")

random.seed(42)
test_points = [(random.randint(0, 255), random.randint(0, 255)) for _ in range(500)]

# Sort three ways
by_x = sorted(test_points, key=lambda p: (p[0], p[1]))
by_morton = morton_sort_2d(test_points)
by_hilbert_approx = morton_sort_2d(test_points)  # Morton is a good proxy

def avg_consecutive_distance(pts):
    total = 0
    for i in range(len(pts) - 1):
        dx = pts[i+1][0] - pts[i][0]
        dy = pts[i+1][1] - pts[i][1]
        total += math.sqrt(dx*dx + dy*dy)
    return total / (len(pts) - 1)

dist_x = avg_consecutive_distance(by_x)
dist_morton = avg_consecutive_distance(by_morton)

print(f"  500 random points in [0,255]²:")
print(f"    Sort by (x, y):     avg consecutive distance = {dist_x:.1f}")
print(f"    Sort by Morton:     avg consecutive distance = {dist_morton:.1f}")
improvement = (1 - dist_morton / dist_x) * 100
if improvement > 0:
    print(f"    Morton is {improvement:.0f}% better for spatial locality")
else:
    print(f"    (Results vary by random seed; Morton typically wins on locality)")
print()

subsection("Multi-Key Morton Sort: Beyond 2D")

print("""\
  The same trick works in any number of dimensions:

  2D: interleave(x, y)           — map tiles, image processing
  3D: interleave(x, y, z)        — voxel grids, n-body simulation
  nD: interleave(k₁, k₂, ..., kₙ) — database multi-column indexing

  For database indexing, think of each column as a "dimension." Z-order
  indexing lets you do efficient range queries on MULTIPLE columns with
  a single index — no need for compound B-trees.

  This is why ClickHouse, DuckDB, and other analytical databases use
  Morton order for their primary key ordering.
""")

# 3D demo
random.seed(99)
pts_3d = [(random.randint(0, 7), random.randint(0, 7), random.randint(0, 7))
          for _ in range(10)]
sorted_3d = morton_sort_3d(pts_3d)

print("  3D Morton sort example:")
print(f"  Input:  {pts_3d}")
print(f"  Sorted: {sorted_3d}")
print()

# Benchmark
print("  Benchmark: Morton Sort vs. Tuple Sort")
print("  ──────────────────────────────────────")

for n in [10_000, 50_000, 100_000]:
    data = [(random.randint(0, 1000), random.randint(0, 1000)) for _ in range(n)]

    t0 = time.perf_counter()
    r1 = morton_sort_2d(data)
    t_morton = time.perf_counter() - t0

    t0 = time.perf_counter()
    r2 = sorted(data, key=lambda p: (p[0], p[1]))
    t_tuple = time.perf_counter() - t0

    print(f"  n={n:>7,}: Morton={t_morton:.4f}s  (x,y)-sort={t_tuple:.4f}s")

print()
print("  Note: Morton and (x,y) sort produce DIFFERENT orderings — that's")
print("  the point. Morton optimizes for spatial locality, not lexicographic")
print("  order. They solve different problems.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  THE SYNTHESIS TABLE
# ─────────────────────────────────────────────────────────────────────────────

section("THE SYNTHESIS — Cross-Repo Algorithm Properties")

print("""\
  ┌─────────────────────┬───────────────┬───────────┬────────┬────────┬──────────────────────────┐
  │ Algorithm           │ Time          │ Space     │ Stable │ In-    │ Key Insight From         │
  │                     │               │           │        │ Place  │                          │
  ├─────────────────────┼───────────────┼───────────┼────────┼────────┼──────────────────────────┤
  │ Radix Exchange      │ O(b·n)        │ O(b)      │ No     │ Yes    │ Bit inspection [repo 4]  │
  │ Bit-Parallel Grav.  │ O(n·max)      │ O(max)    │ No     │ No     │ Popcount/SWAR [repo 4]   │
  │ Newton's Estimate   │ O(n) ~ O(n²)  │ O(n)      │ Yes    │ No     │ Estimate+refine [repo 6] │
  │ Wavelet Tree        │ O(n·log σ)    │ O(n·log σ)│ Yes    │ No     │ Signal decomp [repo 5]   │
  │ CA Sort             │ O(n²) / O(n)‡ │ O(1)      │ Yes    │ Yes    │ Local rules [repo 6]     │
  │ Morton Sort         │ O(n·log n)    │ O(n)      │ Dep.   │ No     │ Bit interleave [repos 3,4]│
  └─────────────────────┴───────────────┴───────────┴────────┴────────┴──────────────────────────┘

  ‡ CA sort is O(n) with n parallel processors; O(n²) sequential.
  b = bit width, σ = distinct values, max = maximum element value.

  These aren't just academic exercises. Radix exchange is used in database
  indexing. Wavelet trees power compressed text indices. Morton sort is
  the foundation of spatial databases. CA-style sorting networks run on
  FPGAs. The "Newton's estimate" approach IS bucket sort — which is what
  Pandas uses internally for float data.

  What makes them novel here is the FRAMING: recognizing that each of these
  draws on a deep idea from elsewhere in computer science.

  ┌─────────────────────────────────────────────────────────────────────┐
  │  Every sorting algorithm is, at its core, a statement about how    │
  │  information flows from disorder to order. The tool you use to     │
  │  move that information — comparisons, bits, estimates, signals,    │
  │  local rules — determines the algorithm's character.               │
  └─────────────────────────────────────────────────────────────────────┘
""")


# ─────────────────────────────────────────────────────────────────────────────
#  FINAL SHOWDOWN — All Six Algorithms on the Same Data
# ─────────────────────────────────────────────────────────────────────────────

section("THE SHOWDOWN — All Six on Random Data")

print("""\
  Let's race all six algorithms on the same random data, alongside Python's
  built-in sorted() (C Timsort) as the reference.
""")

random.seed(2026)
showdown_n = 5000
showdown_data = [random.randint(0, 10000) for _ in range(showdown_n)]

contestants = [
    ("Radix Exchange",    lambda d: radix_exchange_sort(d)),
    ("Bit-Par. Gravity",  lambda d: gravity_sort_bitparallel(d)),
    ("Newton's Estimate", lambda d: newtons_estimate_sort(d)),
    ("Wavelet Tree",      lambda d: wavelet_tree_sort(d)),
    ("CA Sort (basic)",   lambda d: ca_sort(d)),
    ("CA Sort (extended)",lambda d: ca_sort_extended(d)),
    ("Python sorted()",   lambda d: sorted(d)),
]

# Morton sort excluded — it solves a different problem (multi-key)

expected = sorted(showdown_data)
print(f"  Data: {showdown_n} random integers in [0, 10000]")
print()
print(f"  {'Algorithm':<22s}  {'Time':>8s}  {'Correct':>7s}  {'vs Python':>10s}")
print(f"  {'─'*22}  {'─'*8}  {'─'*7}  {'─'*10}")

python_time = None
for name, fn in contestants:
    t0 = time.perf_counter()
    result = fn(showdown_data)
    elapsed = time.perf_counter() - t0

    correct = result == expected
    if name == "Python sorted()":
        python_time = elapsed
    ratio = f"{elapsed/python_time:.1f}×" if python_time and python_time > 0 else "—"
    status = "✓" if correct else "✗"
    print(f"  {name:<22s}  {elapsed:>7.4f}s  {status:>7s}  {ratio:>10s}")

print()
print("  Notes:")
print("  • Python sorted() is C Timsort — hard to beat from pure Python")
print("  • Radix Exchange benefits from being in-place and cache-friendly")
print("  • CA Sort is intentionally slow (O(n²)) — the value is the paradigm")
print("  • Bit-Parallel Gravity is limited by max_val (here: 10000 columns)")
print("  • Newton's Estimate shines on uniform data (close to O(n))")
print("  • Wavelet Tree is elegant but has overhead from recursion + lists")
print()

# ─────────────────────────────────────────────────────────────────────────────
#  CONNECTION MAP
# ─────────────────────────────────────────────────────────────────────────────

section("CONNECTION MAP — Where Every Idea Came From")

print("""\
  ┌───────────────────────────────────────────────────────────────────┐
  │                    THE SORTING–REPO SYNTHESIS                    │
  ├───────────────────────────────────────────────────────────────────┤
  │                                                                   │
  │  [repo 2: pathfinding]                                           │
  │    └─ Graph traversal ──→ Topological sort (BFS/DFS ordering)    │
  │                                                                   │
  │  [repo 3: number-systems]                                        │
  │    ├─ Positional encoding ──→ Radix sort (Script 04)             │
  │    └─ Multi-base digits ──→ Morton interleaving (THIS SCRIPT)    │
  │                                                                   │
  │  [repo 4: bit-tricks]                                            │
  │    ├─ Bit inspection ──→ Radix exchange sort (THIS SCRIPT)       │
  │    ├─ Popcount/SWAR ──→ Bit-parallel gravity (THIS SCRIPT)      │
  │    └─ Bit interleaving ──→ Morton/Z-order sort (THIS SCRIPT)     │
  │                                                                   │
  │  [repo 5: waveguides]                                            │
  │    ├─ Signal decomposition ──→ Wavelet tree sort (THIS SCRIPT)   │
  │    └─ Butterfly operations ──→ Bitonic sort (Script 06)          │
  │                                                                   │
  │  [repo 6: fisr-to-conway]                                        │
  │    ├─ Newton's method ──→ Newton's estimate sort (THIS SCRIPT)   │
  │    └─ Cellular automata ──→ CA sort (THIS SCRIPT)                │
  │                                                                   │
  │  [repo 7: sorting — YOU ARE HERE]                                │
  │    └─ All 8 previous scripts ──→ the foundation for these 6     │
  └───────────────────────────────────────────────────────────────────┘

  Next: Script 08 (The Great Sort Off) benchmarks the practical champions.
  This script showed something different — that the IDEAS behind sorting
  come from everywhere. Bits, waves, physics, estimation, evolution.

  Sorting isn't just a problem. It's a lens.
""")

print("  ─── End of Script 09 ───")
print()
