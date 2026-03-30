#!/usr/bin/env python3
"""
06_parallel_and_network_sorts.py — Sorting When You Have Friends

What if you had 1000 processors? What if your data lived on a million
machines? What if you needed to sort faster than any single computer could?

Sorting networks are circuits made of fixed compare-and-swap operations.
They always work, regardless of input, and they can run comparisons in
parallel. Bitonic sort, one of the most beautiful algorithms in CS,
works by building "bitonic sequences" and recursively merging them.

External sorting handles data sets that don't fit in memory — the kind
of problem Google faces when indexing the web. MapReduce's shuffle phase
is essentially a distributed sort.

This script explores the boundary between algorithms and hardware.

Topics: sorting networks · comparator notation · zero-one principle ·
bitonic sort · odd-even merge · external merge sort · k-way merge ·
parallel prefix · MapReduce shuffle · GPU sorting intuition

[← Connects to: repo 2 (navigational pathfinding) — distributed graphs]
"""

import random
import time
import math
import os

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
#  SORTING NETWORKS — Hardwired Sorting
# ─────────────────────────────────────────────────────────────────────────────

section("SORTING NETWORKS — Hardwired Sorting")

print("""\
  A sorting network is a fixed sequence of compare-and-swap operations.
  No branches, no conditionals, no data-dependent decisions. The same
  comparisons happen regardless of the input.

  Why?  Because hardware loves predictability. No branch mispredictions.
  And comparisons on different wires can happen simultaneously.

  A comparator C(i, j) compares elements at positions i and j, and swaps
  them if they're out of order:

    C(i, j):  if a[i] > a[j]: swap(a[i], a[j])

  A sorting network for n elements is a sequence of comparators that sorts
  ANY input of size n. Not some inputs — ALL inputs.
""")


def compare_and_swap(arr, i, j):
    """The fundamental operation of a sorting network."""
    if arr[i] > arr[j]:
        arr[i], arr[j] = arr[j], arr[i]


def draw_network(n, comparators, label=""):
    """Draw a sorting network as ASCII wire diagram."""
    # Each comparator is (layer, i, j)
    # Organize into parallel layers
    layers = {}
    for layer, i, j in comparators:
        if layer not in layers:
            layers[layer] = []
        layers[layer].append((min(i, j), max(i, j)))

    lines = [f"  Wire {k}: ─" for k in range(n)]

    for layer_num in sorted(layers.keys()):
        comps = layers[layer_num]
        col = [" "] * n
        for lo, hi in comps:
            col[lo] = "┬"
            col[hi] = "┴"
            for k in range(lo + 1, hi):
                if col[k] == " ":
                    col[k] = "│"
        for k in range(n):
            if col[k] in ("┬", "┴"):
                lines[k] += f"─●─"
            elif col[k] == "│":
                lines[k] += f"─│─"
            else:
                lines[k] += f"───"

    for k in range(n):
        lines[k] += "─▸"

    if label:
        print(f"  {label}")
        print()
    for line in lines:
        print(line)
    print()


# Small sorting networks
subsection("Small Networks: Sorting 4 Elements")

# Optimal 4-element network (5 comparators, 3 layers)
network_4 = [
    (0, 0, 1), (0, 2, 3),  # Layer 0: two independent comparisons
    (1, 0, 2), (1, 1, 3),  # Layer 1: two independent comparisons
    (2, 1, 2),              # Layer 2: final comparison
]

draw_network(4, network_4, "Optimal 4-element network (5 comparators, 3 layers)")

# Demonstrate it works
demo = [4, 2, 3, 1]
print(f"  Input:  {demo}")
for _, i, j in network_4:
    compare_and_swap(demo, i, j)
print(f"  Output: {demo}")
print(f"  Sorted: {demo == sorted(demo)} ✓")
print()

# Verify on all possible inputs (permutations)
from itertools import permutations
all_correct = True
for perm in permutations(range(4)):
    test = list(perm)
    for _, i, j in network_4:
        compare_and_swap(test, i, j)
    if test != sorted(test):
        all_correct = False
        break

print(f"  Verified on all 4! = 24 permutations: {'✓ all sorted' if all_correct else '✗ FAILED'}")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  THE ZERO-ONE PRINCIPLE
# ─────────────────────────────────────────────────────────────────────────────

subsection("The Zero-One Principle")

print("""\
  To prove a sorting network is correct, you DON'T need to test all n!
  permutations. You only need to test all 2^n binary sequences (0s and 1s).

  Theorem: If a comparator network sorts all 2^n binary inputs correctly,
  then it sorts ALL inputs correctly.

  Why? Because compare-and-swap preserves the relative order of equal
  elements and can be analyzed monotonically. If it works for {0, 1},
  it works for any linearly ordered set.

  For n = 4:  24 permutations → only 16 binary tests needed.
  For n = 16: 16! ≈ 2×10¹³ permutations → only 65,536 binary tests.
""")

# Prove the 4-element network with zero-one principle
all_binary_correct = True
for bits in range(2**4):
    test = [(bits >> k) & 1 for k in range(4)]
    for _, i, j in network_4:
        compare_and_swap(test, i, j)
    if test != sorted(test):
        all_binary_correct = False
        break

print(f"  4-element network on 2⁴ = 16 binary inputs: {'✓ all sorted' if all_binary_correct else '✗ FAILED'}")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  BITONIC SORT — One of the Most Beautiful Algorithms
# ─────────────────────────────────────────────────────────────────────────────

section("BITONIC SORT — One of the Most Beautiful Algorithms")

print("""\
  Batcher, 1968. The key insight: a "bitonic sequence" is one that first
  increases then decreases (or can be cyclically shifted to have this form).

    Bitonic:     [1, 3, 5, 7, 6, 4, 2]     ↑ then ↓
    Bitonic:     [7, 6, 4, 2, 1, 3, 5]     ↓ then ↑ (cyclic)
    Not bitonic: [1, 5, 3, 7, 2, 4, 6]     no single peak

  Bitonic merge: given a bitonic sequence, split it in half and compare
  corresponding elements. The two halves are both bitonic, AND every
  element in one half ≤ every element in the other.

  Recurse until sorted. The entire algo is:
    1. Build a bitonic sequence (by recursively sorting halves in opposite
       directions)
    2. Bitonic merge it

  Depth: O(log²n).  Comparisons: O(n log²n).  Fully parallelizable.
""")


def bitonic_sort(arr, lo=0, n=None, ascending=True):
    """Bitonic sort: recursive build + merge."""
    if n is None:
        # Pad to power of 2
        n = len(arr)
        next_pow2 = 1
        while next_pow2 < n:
            next_pow2 *= 2
        arr = arr + [float('inf')] * (next_pow2 - n)
        bitonic_sort(arr, 0, next_pow2, ascending)
        return arr[:n]

    if n <= 1:
        return

    mid = n // 2
    # Sort first half ascending, second half descending
    bitonic_sort(arr, lo, mid, not ascending)
    bitonic_sort(arr, lo + mid, mid, ascending)
    # Bitonic merge
    _bitonic_merge(arr, lo, n, ascending)


def _bitonic_merge(arr, lo, n, ascending):
    """Merge a bitonic sequence."""
    if n <= 1:
        return
    mid = n // 2
    for i in range(lo, lo + mid):
        if (arr[i] > arr[i + mid]) == ascending:
            arr[i], arr[i + mid] = arr[i + mid], arr[i]
    _bitonic_merge(arr, lo, mid, ascending)
    _bitonic_merge(arr, lo + mid, mid, ascending)


def bitonic_sort_traced(arr):
    """Bitonic sort with step tracing."""
    n = len(arr)
    next_pow2 = 1
    while next_pow2 < n:
        next_pow2 *= 2
    a = arr[:] + [float('inf')] * (next_pow2 - n)
    size = next_pow2
    steps = []

    def _sort(lo, cnt, ascending):
        if cnt <= 1:
            return
        mid = cnt // 2
        _sort(lo, mid, True)
        _sort(lo + mid, mid, False)
        _merge(lo, cnt, ascending)

    def _merge(lo, cnt, ascending):
        if cnt <= 1:
            return
        mid = cnt // 2
        for i in range(lo, lo + mid):
            if (a[i] > a[i + mid]) == ascending:
                a[i], a[i + mid] = a[i + mid], a[i]
                steps.append(a[:n])
        _merge(lo, mid, ascending)
        _merge(lo + mid, mid, ascending)

    _sort(0, size, True)
    return a[:n], steps


demo = [5, 3, 8, 1, 7, 2, 6, 4]
result, steps = bitonic_sort_traced(demo)
print(f"  Input:  {demo}")
print(f"  Output: {result}")
print(f"  Steps:  {len(steps)} swap operations")
print()

# Visualize as bar chart for small example
def show_bars(arr, width=40, label=""):
    mx = max(arr) if arr else 1
    if label:
        print(f"  {label}")
    for val in arr:
        bar = "█" * int(val / mx * width)
        print(f"  {val:>3d} │{bar}")
    print()

print("  First few steps of bitonic sort on [5, 3, 8, 1, 7, 2, 6, 4]:")
show_bars(demo, width=30, label="Initial:")
for i, step in enumerate(steps[:5]):
    show_bars(step, width=30, label=f"After swap {i+1}:")
show_bars(result, width=30, label="Final:")


# Generate bitonic network comparators for visualization
def bitonic_network(n):
    """Generate comparators for a bitonic sorting network."""
    comparators = []
    layer = [0]

    def _sort(lo, cnt, ascending):
        if cnt <= 1:
            return
        mid = cnt // 2
        _sort(lo, mid, True)
        _sort(lo + mid, mid, False)
        _merge(lo, cnt, ascending)

    def _merge(lo, cnt, ascending):
        if cnt <= 1:
            return
        mid = cnt // 2
        for i in range(lo, lo + mid):
            if ascending:
                comparators.append((layer[0], i, i + mid))
            else:
                comparators.append((layer[0], i + mid, i))
        layer[0] += 1
        _merge(lo, mid, ascending)
        _merge(lo + mid, mid, ascending)

    _sort(0, n, True)
    return comparators

print("  8-element bitonic sorting network:")
comps = bitonic_network(8)
draw_network(8, [(l, min(i,j), max(i,j)) for l,i,j in comps])


# ─────────────────────────────────────────────────────────────────────────────
#  ODD-EVEN MERGE SORT
# ─────────────────────────────────────────────────────────────────────────────

section("ODD-EVEN MERGE SORT — Batcher's Other Gem")

print("""\
  Also by Batcher, 1968. A different approach to building a sorting network.

  Odd-even merge: to merge two sorted halves, recursively merge the
  odd-indexed elements and even-indexed elements separately, then do one
  final pass of compare-and-swap on adjacent pairs.

  Same O(n log²n) comparisons, O(log²n) depth — but the structure is
  different and sometimes more hardware-friendly.
""")


def odd_even_merge_sort(arr):
    """Batcher's odd-even merge sort."""
    arr = arr[:]
    n = len(arr)

    # Pad to power of 2
    next_pow2 = 1
    while next_pow2 < n:
        next_pow2 *= 2
    arr.extend([float('inf')] * (next_pow2 - n))

    def _oe_sort(lo, hi):
        if hi - lo <= 1:
            return
        mid = (lo + hi) // 2
        _oe_sort(lo, mid)
        _oe_sort(mid, hi)
        _oe_merge(lo, hi, 1)

    def _oe_merge(lo, hi, step):
        size = hi - lo
        if step >= size:
            return
        if step * 2 >= size:
            compare_and_swap(arr, lo, lo + step)
            return
        _oe_merge(lo, hi, step * 2)
        _oe_merge(lo + step, hi, step * 2)
        i = lo + step
        while i + step < hi:
            compare_and_swap(arr, i, i + step)
            i += step * 2

    _oe_sort(0, next_pow2)
    return arr[:n]


demo = [7, 3, 5, 1, 8, 2, 6, 4]
result = odd_even_merge_sort(demo)
print(f"  Input:  {demo}")
print(f"  Output: {result}")
print(f"  Correct: {result == sorted(demo)} ✓")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  PARALLEL SORT SIMULATION
# ─────────────────────────────────────────────────────────────────────────────

section("PARALLEL SORTING — What If You Had 1000 Processors?")

print("""\
  Sorting networks are significant because their DEPTH determines the time
  on a parallel machine. Each layer's comparisons run simultaneously.

  ┌──────────────────────┬───────────────┬──────────────┬───────────────┐
  │ Network              │  Comparisons  │    Depth     │  Processors   │
  ├──────────────────────┼───────────────┼──────────────┼───────────────┤
  │ Bitonic sort         │ O(n log²n)    │  O(log²n)    │ O(n)          │
  │ Odd-even merge       │ O(n log²n)    │  O(log²n)    │ O(n)          │
  │ AKS network (1983)   │ O(n log n)    │  O(log n)    │ O(n)          │
  └──────────────────────┴───────────────┴──────────────┴───────────────┘

  The AKS network is OPTIMAL in depth — O(log n) — but the constant is so
  large it's never been implemented in practice. It proves that optimal
  parallel sorting is POSSIBLE, even if nobody actually does it.

  For GPUs, bitonic sort is the go-to: its regular structure maps perfectly
  to SIMD lanes and warp-level operations.
""")


# Simulate parallel execution
def simulate_parallel_sort(n, network_type="bitonic"):
    """Simulate parallel bitonic sort and count parallel steps."""
    # For bitonic sort of n elements
    # Depth = (log n)(log n + 1) / 2
    log_n = math.ceil(math.log2(n)) if n > 1 else 1
    depth = log_n * (log_n + 1) // 2
    total_comparisons = n * log_n * (log_n + 1) // 4  # approximately
    return depth, total_comparisons

print(f"  {'n':>10s}  {'Depth (par. time)':>18s}  {'Total comparisons':>20s}  {'Speedup':>10s}")
print(f"  {'─'*10}  {'─'*18}  {'─'*20}  {'─'*10}")
for exp in range(4, 21, 2):
    n = 2 ** exp
    depth, total = simulate_parallel_sort(n)
    serial = n * math.log2(n) if n > 1 else 0
    speedup = serial / depth if depth > 0 else 0
    print(f"  {n:>10,}  {depth:>18,}  {total:>20,}  {speedup:>9.0f}×")

print()
print("  With enough processors, sorting a million elements takes only ~210 parallel steps.")
print("  That's the power of sorting networks on parallel hardware.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  EXTERNAL SORT — When Data Doesn't Fit in RAM
# ─────────────────────────────────────────────────────────────────────────────

section("EXTERNAL SORT — When Data Doesn't Fit in RAM")

print("""\
  What if you need to sort 1 TB of data with 16 GB of RAM?

  External merge sort:
    1. Read chunks that fit in RAM (16 GB each)
    2. Sort each chunk in memory (using Timsort, quicksort, etc.)
    3. Write sorted chunks to disk ("runs")
    4. K-way merge the sorted runs

  Phase 1: Create sorted runs
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │  Chunk 1   │  │  Chunk 2   │  │  Chunk 3   │  ...  64 chunks
    │  sorted    │  │  sorted    │  │  sorted    │
    └────────────┘  └────────────┘  └────────────┘

  Phase 2: K-way merge
    Read one buffer from each of K runs.
    Use a min-heap to find the smallest element across all K runs.
    Output it. Refill the buffer when it empties.

  I/O complexity: O((n/B) · log_{M/B}(n/M))
    n = total data, B = block size, M = memory size.
    The log base is M/B, not 2 — each pass merges M/B runs.
""")


def simulate_external_sort(total_bytes, ram_bytes, block_bytes=4096):
    """Simulate external merge sort statistics."""
    num_initial_runs = math.ceil(total_bytes / ram_bytes)
    k = ram_bytes // block_bytes  # max k-way merge
    passes = math.ceil(math.log(num_initial_runs) / math.log(k)) if num_initial_runs > 1 and k > 1 else 0

    total_io_bytes = total_bytes * (1 + passes) * 2  # read + write each pass

    return {
        "initial_runs": num_initial_runs,
        "merge_ways": k,
        "merge_passes": passes,
        "total_io": total_io_bytes,
    }

def fmt_bytes(b):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if b < 1024:
            return f"{b:.0f} {unit}"
        b /= 1024
    return f"{b:.0f} EB"


print(f"  {'Total Data':>12s}  {'RAM':>8s}  {'Runs':>6s}  {'K-way':>6s}  {'Passes':>7s}  {'Total I/O':>12s}")
print(f"  {'─'*12}  {'─'*8}  {'─'*6}  {'─'*6}  {'─'*7}  {'─'*12}")

scenarios = [
    (1 * 2**30, 256 * 2**20),    # 1 GB with 256 MB RAM
    (10 * 2**30, 1 * 2**30),     # 10 GB with 1 GB RAM
    (100 * 2**30, 4 * 2**30),    # 100 GB with 4 GB RAM
    (1 * 2**40, 16 * 2**30),     # 1 TB with 16 GB RAM
    (10 * 2**40, 64 * 2**30),    # 10 TB with 64 GB RAM
]

for total, ram in scenarios:
    stats = simulate_external_sort(total, ram)
    print(f"  {fmt_bytes(total):>12s}  {fmt_bytes(ram):>8s}  {stats['initial_runs']:>6d}  "
          f"{stats['merge_ways']:>6,}  {stats['merge_passes']:>7d}  {fmt_bytes(stats['total_io']):>12s}")

print()
print("  Key insight: high fan-out (many-way merge) reduces passes.")
print("  With 16 GB RAM and 4 KB blocks, you can do a 4096-way merge —")
print("  so even 1 TB sorts in just 1 merge pass after creating runs.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  K-WAY MERGE WITH A HEAP
# ─────────────────────────────────────────────────────────────────────────────

subsection("K-Way Merge Using a Min-Heap")

print("""\
  The heart of external sorting is the k-way merge. We use a min-heap
  that holds one element from each of the k sorted runs.

  Pop the minimum, output it, and push the next element from that same run.
  This gives O(n log k) time for merging n total elements from k runs.
""")

import heapq

def k_way_merge(runs):
    """Merge k sorted lists using a min-heap."""
    heap = []
    output = []

    # Initialize heap with first element of each run
    for run_idx, run in enumerate(runs):
        if run:
            heapq.heappush(heap, (run[0], run_idx, 0))

    while heap:
        val, run_idx, elem_idx = heapq.heappop(heap)
        output.append(val)

        # Push next element from same run
        if elem_idx + 1 < len(runs[run_idx]):
            next_val = runs[run_idx][elem_idx + 1]
            heapq.heappush(heap, (next_val, run_idx, elem_idx + 1))

    return output


# Demo
runs = [
    [1, 5, 9, 13],
    [2, 6, 10, 14],
    [3, 7, 11, 15],
    [4, 8, 12, 16],
]

print("  Sorted runs:")
for i, run in enumerate(runs):
    print(f"    Run {i}: {run}")

result = k_way_merge(runs)
print(f"\n  Merged: {result}")
print(f"  Correct: {result == sorted(result)} ✓")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  MAPREDUCE SHUFFLE — Distributed Sorting
# ─────────────────────────────────────────────────────────────────────────────

section("MAPREDUCE SHUFFLE — Sorting the Internet")

print("""\
  When Google indexes the web, they need to sort data across thousands of
  machines. MapReduce (2004) uses a distributed sort as its core operation.

  The three phases:
    MAP     → Each machine processes its local data, emitting (key, value) pairs
    SHUFFLE → The system SORTS and routes all pairs by key across the network
    REDUCE  → Each machine processes all values for its assigned key range

  The shuffle phase is a distributed sort:
    1. Each mapper sorts its output by key
    2. Partitioner assigns keys to reducers (hash(key) % num_reducers)
    3. Each reducer receives sorted chunks from all mappers
    4. Reducer does a k-way merge of these sorted chunks

  This is external sort at planetary scale.

  Simulating a mini MapReduce word-count with sort:
""")


def mini_mapreduce_sort(documents, num_mappers=3, num_reducers=2):
    """Simulate a MapReduce-style distributed sort."""
    print(f"  {num_mappers} mappers, {num_reducers} reducers\n")

    # Split documents across mappers
    chunks = [[] for _ in range(num_mappers)]
    for i, doc in enumerate(documents):
        chunks[i % num_mappers].append(doc)

    # MAP phase: each mapper emits (word, 1) sorted by word
    print("  MAP phase:")
    mapper_outputs = []
    for m in range(num_mappers):
        words = []
        for doc in chunks[m]:
            words.extend(doc.lower().split())
        pairs = sorted([(w, 1) for w in words])
        mapper_outputs.append(pairs)
        preview = pairs[:3]
        print(f"    Mapper {m}: {preview}{'...' if len(pairs) > 3 else ''} ({len(pairs)} pairs)")

    # SHUFFLE phase: sort and partition by key
    print("\n  SHUFFLE phase (the distributed sort):")
    reducer_inputs = [[] for _ in range(num_reducers)]
    for pairs in mapper_outputs:
        for word, count in pairs:
            r = hash(word) % num_reducers
            reducer_inputs[r].append((word, count))

    # Each reducer sorts its input (k-way merge of sorted mapper outputs)
    for r in range(num_reducers):
        reducer_inputs[r].sort()
        preview = reducer_inputs[r][:3]
        print(f"    Reducer {r} receives: {preview}{'...' if len(reducer_inputs[r]) > 3 else ''}")

    # REDUCE phase: aggregate
    print("\n  REDUCE phase:")
    final = {}
    for r in range(num_reducers):
        for word, count in reducer_inputs[r]:
            final[word] = final.get(word, 0) + count

    top_words = sorted(final.items(), key=lambda x: -x[1])[:10]
    for word, count in top_words:
        bar = "█" * count
        print(f"    {word:>12s}: {bar} ({count})")

    return final


documents = [
    "the quick brown fox jumps over the lazy dog",
    "the dog barked at the fox and the fox ran away",
    "sorting is the fundamental operation of computer science",
    "the fox and the dog went to sort the data together",
    "parallel sorting networks can sort data on many machines",
]

mini_mapreduce_sort(documents)
print()


# ─────────────────────────────────────────────────────────────────────────────
#  BENCHMARKS: SORTING NETWORKS VS. COMPARISON SORTS
# ─────────────────────────────────────────────────────────────────────────────

section("BENCHMARKS: Networks vs. Comparison Sorts")

n = 4096
random.seed(42)
data = random.sample(range(n * 10), n)

print(f"  n = {n:,}, random data\n")
print(f"  {'Algorithm':>20s}  {'Time':>10s}  {'Correct':>8s}")
print(f"  {'─'*20}  {'─'*10}  {'─'*8}")

# Bitonic sort
d = data[:]
t0 = time.perf_counter()
result = bitonic_sort(d)
elapsed = time.perf_counter() - t0
print(f"  {'Bitonic sort':>20s}  {elapsed:>9.4f}s  {'✓' if result == sorted(data) else '✗':>8s}")

# Odd-even merge sort
d = data[:]
t0 = time.perf_counter()
result = odd_even_merge_sort(d)
elapsed = time.perf_counter() - t0
print(f"  {'Odd-even merge':>20s}  {elapsed:>9.4f}s  {'✓' if result == sorted(data) else '✗':>8s}")

# Python sorted (Timsort)
d = data[:]
t0 = time.perf_counter()
result = sorted(d)
elapsed = time.perf_counter() - t0
print(f"  {'Python Timsort':>20s}  {elapsed:>9.4f}s  {'✓':>8s}")

print()
print("  Network sorts are slower in serial (O(n log²n) vs O(n log n)).")
print("  Their value is in PARALLEL execution: O(log²n) depth.")
print("  A bitonic sort on a GPU with n processors runs in O(log²n) time.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

section("PARALLEL AND NETWORK SORTS: SUMMARY")

print("""\
  ┌──────────────────┬──────────────┬──────────┬─────────────────────────┐
  │ Algorithm        │  Serial Time │  Depth   │ Use Case                │
  ├──────────────────┼──────────────┼──────────┼─────────────────────────┤
  │ Bitonic sort     │  O(n log²n)  │ O(log²n) │ GPU sorting, FPGA       │
  │ Odd-even merge   │  O(n log²n)  │ O(log²n) │ Hardware sorting nets    │
  │ AKS network      │  O(n log n)  │ O(log n) │ Theoretical optimality  │
  │ External merge   │  O(n log n)* │   N/A    │ Data > RAM              │
  │ MapReduce sort   │  distributed │   N/A    │ Planetary-scale data    │
  └──────────────────┴──────────────┴──────────┴─────────────────────────┘
                                     * plus I/O cost

  The hierarchy of sorting scale:
    • Small data:    Insertion sort, hybrid (Timsort/Introsort)
    • RAM-sized:     Quicksort, merge sort
    • Bigger-than-RAM: External merge sort
    • Cluster-sized: Distributed sort (MapReduce/Spark)
    • GPU:           Sorting networks (bitonic, merge networks)

  Each level up changes not just the algorithm but the COMPUTATIONAL MODEL.
  Sorting isn't one problem — it's a family of problems, depending on
  where your data lives and how many processors you have.

  Next up: the algorithms that sort for fun, not efficiency.
""")

print("  ─── End of Script 06 ───")
print()
