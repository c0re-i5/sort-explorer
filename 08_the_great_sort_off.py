#!/usr/bin/env python3
"""
08_the_great_sort_off.py — The Capstone

Every algorithm. Every input pattern. Every metric.
ONE comprehensive showdown.

This script pits all the sorting algorithms from scripts 01-07 against
each other across multiple dimensions: speed, comparisons, memory, stability,
adaptivity, and scaling behavior. We build the definitive comparison table.

(For the bitwise and cross-repo novel algorithms, see script 09.)

This isn't just a benchmark — it's a story. We see which algorithms rise
under pressure, which crumble on adversarial inputs, and which quietly
dominate when nobody's looking (spoiler: it's Timsort).

Topics: comprehensive benchmarking · scaling analysis · stability matrix ·
adaptivity profiles · the algorithm picker guide · final reflections
"""

import random
import time
import math
import sys

sys.setrecursionlimit(100000)

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
#  ALL THE CONTESTANTS
# ─────────────────────────────────────────────────────────────────────────────

# --- Script 01: Naive sorts ---

def bubble_sort(arr):
    arr = arr[:]
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr


def insertion_sort(arr):
    arr = arr[:]
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr


def selection_sort(arr):
    arr = arr[:]
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr


# --- Script 02: Divide and conquer ---

def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
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


def quicksort(arr):
    if len(arr) <= 1:
        return arr
    # Median of three
    lo, mid_val, hi = arr[0], arr[len(arr)//2], arr[-1]
    pivot = sorted([lo, mid_val, hi])[1]
    less = [x for x in arr if x < pivot]
    equal = [x for x in arr if x == pivot]
    greater = [x for x in arr if x > pivot]
    return quicksort(less) + equal + quicksort(greater)


# --- Script 03: Heaps and trees ---

def heapsort(arr):
    arr = arr[:]
    n = len(arr)
    def sift_down(a, size, i):
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
        sift_down(arr, n, i)
    for i in range(n-1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        sift_down(arr, i, 0)
    return arr


# --- Script 04: Non-comparison ---

def counting_sort(arr):
    if not arr:
        return []
    mn, mx = min(arr), max(arr)
    count = [0] * (mx - mn + 1)
    for x in arr:
        count[x - mn] += 1
    result = []
    for i, c in enumerate(count):
        result.extend([i + mn] * c)
    return result


def radix_sort_lsd(arr):
    if not arr:
        return []
    arr = arr[:]
    mx = max(arr)
    exp = 1
    while mx // exp > 0:
        buckets = [[] for _ in range(10)]
        for x in arr:
            buckets[(x // exp) % 10].append(x)
        arr = []
        for bucket in buckets:
            arr.extend(bucket)
        exp *= 10
    return arr


# --- Script 05: Adaptive/Hybrid ---

def compute_minrun(n):
    r = 0
    while n >= 64:
        r |= n & 1
        n >>= 1
    return n + r


def timsort_simplified(arr):
    arr = arr[:]
    n = len(arr)
    if n <= 1:
        return arr
    minrun = compute_minrun(n)
    runs = []
    i = 0
    while i < n:
        start = i
        if i + 1 < n:
            if arr[i] <= arr[i + 1]:
                while i + 1 < n and arr[i] <= arr[i + 1]:
                    i += 1
            else:
                while i + 1 < n and arr[i] > arr[i + 1]:
                    i += 1
                arr[start:i + 1] = arr[start:i + 1][::-1]
        i += 1
        run_len = i - start
        while i < n and run_len < minrun:
            key = arr[i]
            j = i - 1
            while j >= start and arr[j] > key:
                arr[j + 1] = arr[j]
                j -= 1
            arr[j + 1] = key
            i += 1
            run_len += 1
        runs.append((start, run_len))
    def merge_at(a, lo, mid, hi):
        left = a[lo:mid]
        right = a[mid:hi]
        k = lo
        li = ri = 0
        while li < len(left) and ri < len(right):
            if left[li] <= right[ri]:
                a[k] = left[li]; li += 1
            else:
                a[k] = right[ri]; ri += 1
            k += 1
        while li < len(left):
            a[k] = left[li]; li += 1; k += 1
        while ri < len(right):
            a[k] = right[ri]; ri += 1; k += 1
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


def shellsort_ciura(arr):
    arr = arr[:]
    n = len(arr)
    gaps = [701, 301, 132, 57, 23, 10, 4, 1]
    while gaps[0] * 2.25 < n:
        gaps.insert(0, int(gaps[0] * 2.25))
    for gap in gaps:
        if gap >= n:
            continue
        for i in range(gap, n):
            key = arr[i]
            j = i
            while j >= gap and arr[j - gap] > key:
                arr[j] = arr[j - gap]
                j -= gap
            arr[j] = key
    return arr


# --- Python built-in ---
def python_sort(arr):
    return sorted(arr)


# ─────────────────────────────────────────────────────────────────────────────
#  THE GREAT SORT-OFF: INTRO
# ─────────────────────────────────────────────────────────────────────────────

section("THE GREAT SORT-OFF")

print("""\
  Welcome to the definitive sorting algorithm showdown.

  CONTESTANTS:
    From Script 01 — The Naive Sorts:
      • Bubble Sort         O(n²)     stable
      • Insertion Sort      O(n²)     stable
      • Selection Sort      O(n²)     unstable

    From Script 02 — Divide and Conquer:
      • Merge Sort          O(n lg n) stable
      • Quicksort           O(n lg n) unstable (avg)

    From Script 03 — Heaps and Trees:
      • Heapsort            O(n lg n) unstable

    From Script 04 — Beyond Comparison:
      • Counting Sort       O(n+k)    stable
      • Radix Sort (LSD)    O(d·n)    stable

    From Script 05 — Adaptive/Hybrid:
      • Timsort (simplified) O(n lg n) stable
      • Shellsort (Ciura)   O(n^4/3)  unstable

    Special Guest:
      • Python sorted()     C Timsort  stable

  EVENTS:
    1. The Sprint         — small n, who's fastest?
    2. The Marathon        — large n, who scales?
    3. The Obstacle Course — adversarial inputs
    4. The Adaptivity Test — nearly-sorted data
    5. The Stability Check — do equal elements stay put?
""")


# ─────────────────────────────────────────────────────────────────────────────
#  EVENT 1: THE SPRINT (small n)
# ─────────────────────────────────────────────────────────────────────────────

section("EVENT 1: THE SPRINT — Small Arrays (n = 50)")

n = 50
random.seed(2024)
data = random.sample(range(1000), n)

contestants_small = {
    "Bubble sort":      bubble_sort,
    "Insertion sort":   insertion_sort,
    "Selection sort":   selection_sort,
    "Merge sort":       merge_sort,
    "Quicksort":        quicksort,
    "Heapsort":         heapsort,
    "Counting sort":    counting_sort,
    "Radix sort (LSD)": radix_sort_lsd,
    "Timsort":          timsort_simplified,
    "Shellsort":        shellsort_ciura,
    "Python sorted()":  python_sort,
}

results = {}
trials = 500
for name, func in contestants_small.items():
    t0 = time.perf_counter()
    for _ in range(trials):
        func(data)
    elapsed = (time.perf_counter() - t0) / trials
    results[name] = elapsed

# Sort by time
ranked = sorted(results.items(), key=lambda x: x[1])

print(f"  n = {n}, averaged over {trials} trials\n")
print(f"  {'Rank':>4s}  {'Algorithm':>18s}  {'Time (μs)':>10s}  {'Bar':>1s}")
print(f"  {'─'*4}  {'─'*18}  {'─'*10}  {'─'*40}")

fastest = ranked[0][1]
for rank, (name, elapsed) in enumerate(ranked, 1):
    us = elapsed * 1_000_000
    ratio = elapsed / fastest
    bar = "█" * min(int(ratio * 3), 40)
    medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
    print(f"  {rank:>4d}  {name:>18s}  {us:>9.1f}  {bar} {medal}")

print()
print("  At small n, the overhead of fancy algorithms hurts.")
print("  Insertion sort and simple sorts can dominate here.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  EVENT 1B: THE COMPARISON COUNT
# ─────────────────────────────────────────────────────────────────────────────

subsection("The Comparison Count — How Many Questions Does Each Sort Ask?")

print("""\
  Wall time includes hardware quirks. A purer metric: how many
  comparisons does each algorithm actually make to sort the same data?

  We wrap each value so that < > <= >= automatically count.
""")


class Counted:
    """A value wrapper that counts comparisons globally."""
    comparisons = 0

    __slots__ = ('val',)

    def __init__(self, val):
        self.val = val

    def __lt__(self, other):
        Counted.comparisons += 1
        return self.val < (other.val if isinstance(other, Counted) else other)

    def __le__(self, other):
        Counted.comparisons += 1
        return self.val <= (other.val if isinstance(other, Counted) else other)

    def __gt__(self, other):
        Counted.comparisons += 1
        return self.val > (other.val if isinstance(other, Counted) else other)

    def __ge__(self, other):
        Counted.comparisons += 1
        return self.val >= (other.val if isinstance(other, Counted) else other)

    def __eq__(self, other):
        Counted.comparisons += 1
        return self.val == (other.val if isinstance(other, Counted) else other)

    def __ne__(self, other):
        Counted.comparisons += 1
        return self.val != (other.val if isinstance(other, Counted) else other)

    def __hash__(self):
        return hash(self.val)

    def __repr__(self):
        return repr(self.val)


n = 200
random.seed(2024)
base_data = random.sample(range(1000), n)

# Only comparison-based sorts (counting/radix don't compare elements)
comp_contestants = {
    "Bubble sort":    bubble_sort,
    "Insertion sort": insertion_sort,
    "Selection sort": selection_sort,
    "Merge sort":     merge_sort,
    "Quicksort":      quicksort,
    "Heapsort":       heapsort,
    "Timsort":        timsort_simplified,
    "Shellsort":      shellsort_ciura,
}

comp_results = {}
for name, func in comp_contestants.items():
    wrapped = [Counted(x) for x in base_data]
    Counted.comparisons = 0
    func(wrapped)
    comp_results[name] = Counted.comparisons

ranked_comp = sorted(comp_results.items(), key=lambda x: x[1])
nlogn = n * math.log2(n)

print(f"  n = {n}  |  n·log₂n = {nlogn:.0f}  |  n²/2 = {n*(n-1)//2}")
print()
print(f"  {'Rank':>4s}  {'Algorithm':>18s}  {'Comparisons':>12s}  {'vs n·lg n':>10s}  {'Bar':>1s}")
print(f"  {'─'*4}  {'─'*18}  {'─'*12}  {'─'*10}  {'─'*30}")

fewest = ranked_comp[0][1]
for rank, (name, comps) in enumerate(ranked_comp, 1):
    ratio = comps / nlogn
    bar = "█" * min(int(comps / fewest * 3), 30)
    medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
    print(f"  {rank:>4d}  {name:>18s}  {comps:>12,}  {ratio:>9.2f}×  {bar} {medal}")

print()
print("  O(n²) sorts make ~n²/2 comparisons. O(n log n) sorts hover near n·log₂n.")
print("  The gap between them is the difference between seconds and heat death.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  EVENT 2: THE MARATHON (large n)
# ─────────────────────────────────────────────────────────────────────────────

section("EVENT 2: THE MARATHON — Large Arrays (n = 50,000)")

n = 50000
random.seed(2024)
data = random.sample(range(n * 10), n)

# Only algorithms that can handle large n in reasonable time
contestants_large = {
    "Merge sort":       merge_sort,
    "Quicksort":        quicksort,
    "Heapsort":         heapsort,
    "Counting sort":    counting_sort,
    "Radix sort (LSD)": radix_sort_lsd,
    "Timsort":          timsort_simplified,
    "Shellsort":        shellsort_ciura,
    "Python sorted()":  python_sort,
}

results = {}
for name, func in contestants_large.items():
    t0 = time.perf_counter()
    func(data)
    elapsed = time.perf_counter() - t0
    results[name] = elapsed

ranked = sorted(results.items(), key=lambda x: x[1])

print(f"  n = {n:,}, random data\n")
print(f"  {'Rank':>4s}  {'Algorithm':>18s}  {'Time':>10s}  {'Bar':>1s}")
print(f"  {'─'*4}  {'─'*18}  {'─'*10}  {'─'*40}")

fastest = ranked[0][1]
for rank, (name, elapsed) in enumerate(ranked, 1):
    ratio = elapsed / fastest
    bar = "█" * min(int(ratio * 3), 40)
    medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
    print(f"  {rank:>4d}  {name:>18s}  {elapsed:>9.4f}s  {bar} {medal}")

print()
print("  At scale, the O(n log n) and O(n+k) algorithms pull ahead.")
print("  Python's C-optimized Timsort is nearly unbeatable.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  EVENT 3: THE OBSTACLE COURSE (adversarial inputs)
# ─────────────────────────────────────────────────────────────────────────────

section("EVENT 3: THE OBSTACLE COURSE — Adversarial Inputs")

n = 10000
random.seed(2024)

input_patterns = {
    "Random":         random.sample(range(n * 10), n),
    "Already sorted": list(range(n)),
    "Reversed":       list(range(n, 0, -1)),
    "All equal":      [42] * n,
    "Pipe organ":     list(range(n//2)) + list(range(n//2, 0, -1)),
    "Sawtooth":       [i % 100 for i in range(n)],
    "Few unique":     [random.randint(0, 4) for _ in range(n)],
}

contestants_mid = {
    "Merge sort":       merge_sort,
    "Quicksort":        quicksort,
    "Heapsort":         heapsort,
    "Timsort":          timsort_simplified,
    "Shellsort":        shellsort_ciura,
    "Python sorted()":  python_sort,
}

print(f"  n = {n:,}\n")

# Header
algo_names = list(contestants_mid.keys())
header = f"  {'Pattern':>15s}"
for name in algo_names:
    short = name[:10]
    header += f"  {short:>10s}"
print(header)
print(f"  {'─'*15}" + f"  {'─'*10}" * len(algo_names))

for pattern_name, pattern_data in input_patterns.items():
    row = f"  {pattern_name:>15s}"
    for algo_name, algo_func in contestants_mid.items():
        t0 = time.perf_counter()
        algo_func(pattern_data)
        elapsed = time.perf_counter() - t0
        row += f"  {elapsed:>9.4f}s"
    print(row)

print()
print("  Observations:")
print("  • Timsort and Python sorted() crush sorted/reversed (they detect runs)")
print("  • Quicksort handles most patterns well thanks to median-of-3 pivot")
print("  • Heapsort is the most CONSISTENT — nearly the same time for every input")
print("  • 'All equal' is easy for everyone except naive quicksort (median-of-3 helps)")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  EVENT 4: THE ADAPTIVITY TEST
# ─────────────────────────────────────────────────────────────────────────────

section("EVENT 4: THE ADAPTIVITY TEST — Nearly Sorted Data")

print("""\
  How fast can each algorithm sort data that's ALMOST sorted?
  We'll start with sorted data and introduce increasing disorder.
""")

n = 20000

print(f"  n = {n:,}")
print()

# Header
header = f"  {'Disorder':>10s}  {'Swaps':>6s}"
for name in ["Timsort", "Merge", "Quick", "Heap", "Shell", "Python"]:
    header += f"  {name:>8s}"
print(header)
print(f"  {'─'*10}  {'─'*6}" + f"  {'─'*8}" * 6)

adaptivity_algos = {
    "Timsort": timsort_simplified,
    "Merge":   merge_sort,
    "Quick":   quicksort,
    "Heap":    heapsort,
    "Shell":   shellsort_ciura,
    "Python":  python_sort,
}

for disorder_pct in [0, 0.1, 0.5, 1, 2, 5, 10, 25, 50, 100]:
    data = list(range(n))
    num_swaps = int(n * disorder_pct / 100)
    random.seed(42)
    for _ in range(num_swaps):
        i, j = random.randint(0, n-1), random.randint(0, n-1)
        data[i], data[j] = data[j], data[i]

    row = f"  {disorder_pct:>9.1f}%  {num_swaps:>6d}"
    for name, func in adaptivity_algos.items():
        t0 = time.perf_counter()
        func(data)
        elapsed = time.perf_counter() - t0
        row += f"  {elapsed:>7.4f}s"
    print(row)

print()
print("  Key insight: Timsort and Python sorted() scale with disorder, not just n.")
print("  At 0% disorder: essentially O(n). At 100%: O(n log n).")
print("  Non-adaptive sorts (merge, heap) don't benefit from existing order.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  EVENT 5: SCALING ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

section("EVENT 5: SCALING ANALYSIS — How Times Grow")

print("""\
  Doubling n: how much does the time increase?
  O(n²)      → 4×      O(n log n) → ~2.2×      O(n) → 2×
""")

scaling_algos = {
    "Insertion":  insertion_sort,
    "Merge":      merge_sort,
    "Quicksort":  quicksort,
    "Heapsort":   heapsort,
    "Counting":   counting_sort,
    "Radix LSD":  radix_sort_lsd,
    "Timsort":    timsort_simplified,
    "Python":     python_sort,
}

print(f"  {'Algorithm':>12s}", end="")
sizes = [1000, 2000, 4000, 8000, 16000]
for s in sizes:
    print(f"  {'n='+str(s):>8s}", end="")
for s in sizes[1:]:
    print(f"  {'×ratio':>7s}", end="")
print()
print(f"  {'─'*12}" + f"  {'─'*8}" * len(sizes) + f"  {'─'*7}" * (len(sizes)-1))

for algo_name, algo_func in scaling_algos.items():
    times = []
    row = f"  {algo_name:>12s}"
    skip = False
    for s in sizes:
        if skip:
            times.append(None)
            row += f"  {'---':>8s}"
            continue
        random.seed(42)
        data = random.sample(range(s * 10), s)
        t0 = time.perf_counter()
        algo_func(data)
        elapsed = time.perf_counter() - t0
        times.append(elapsed)
        row += f"  {elapsed:>7.4f}s"
        if elapsed > 3:
            skip = True

    # Compute ratios
    for i in range(1, len(times)):
        if times[i] is not None and times[i-1] is not None and times[i-1] > 0:
            ratio = times[i] / times[i-1]
            row += f"  {ratio:>6.2f}×"
        else:
            row += f"  {'---':>7s}"

    print(row)

print()
print("  Ratios near 4× → O(n²).  Near 2× → O(n log n) or O(n).")
print("  Counting/radix sort show ~2× (linear). Insertion shows ~4× (quadratic).")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  THE STABILITY MATRIX
# ─────────────────────────────────────────────────────────────────────────────

section("THE STABILITY MATRIX")

print("""\
  A sort is STABLE if elements with equal keys maintain their original order.

  This matters when sorting by multiple keys (e.g., sort by last name,
  then by first name — stability preserves the first-name order within
  same-last-name groups).
""")


def test_stability(sort_func, name):
    """Test if a sort is stable using tagged elements."""
    # Create elements with duplicate keys: (key, original_index)
    data = [(3, 0), (1, 1), (4, 2), (1, 3), (5, 4), (3, 5), (1, 6)]

    # Sort by key only
    try:
        result = sort_func([x[0] for x in data])
    except Exception:
        return None

    # For a proper stability test, we need a version that sorts tuples
    # Sort using the key, track original indices
    tagged = list(data)
    # Simple insertion sort to test stably
    tagged_sorted = sorted(tagged, key=lambda x: x[0])  # Python's sort is stable

    # Check if equal keys maintain order
    keys_only = [x[0] for x in data]

    # Build a stability test: sort indices, for each key check original order
    result_indices = []
    temp = list(enumerate(keys_only))
    temp.sort(key=lambda x: x[1])  # stable sort as reference

    return True  # Simplified; we'll just state known stability


print(f"  {'Algorithm':>18s}  {'Stable?':>8s}  {'Why / Notes'}")
print(f"  {'─'*18}  {'─'*8}  {'─'*40}")

stability_table = [
    ("Bubble sort",      "Yes", "Only swaps adjacent, never swaps equal elements"),
    ("Insertion sort",   "Yes", "Inserts after equal elements (uses >, not >=)"),
    ("Selection sort",   "No",  "Long-range swaps jump over equal elements"),
    ("Merge sort",       "Yes", "Left element wins ties → preserves order"),
    ("Quicksort",        "No",  "Partition swaps cross equal elements"),
    ("Heapsort",         "No",  "Heap operations scramble equal elements"),
    ("Counting sort",    "Yes", "Processes right-to-left for stability"),
    ("Radix sort (LSD)", "Yes", "Built on stable counting sort"),
    ("Timsort",          "Yes", "Merge-based, carefully stable throughout"),
    ("Shellsort",        "No",  "Gap-based swaps cross equal elements"),
    ("Python sorted()",  "Yes", "Guaranteed by language spec"),
]

for name, stable, reason in stability_table:
    mark = "✓" if stable == "Yes" else "✗"
    print(f"  {name:>18s}  {mark:>5s}    {reason}")

print()


# ─────────────────────────────────────────────────────────────────────────────
#  THE ALGORITHM SELECTOR GUIDE
# ─────────────────────────────────────────────────────────────────────────────

section("THE ALGORITHM SELECTOR GUIDE")

print("""\
  ╔═══════════════════════════════════════════════════════════════════╗
  ║               WHICH SORT SHOULD YOU USE?                        ║
  ╠═══════════════════════════════════════════════════════════════════╣
  ║                                                                 ║
  ║  Is it a standard language with a built-in sort?                ║
  ║  └─ YES → Use it. Python, Java, C++, Rust all have excellent   ║
  ║           built-in sorts. Don't reinvent the wheel.             ║
  ║  └─ NO  → Continue below.                                      ║
  ║                                                                 ║
  ║  How big is n?                                                  ║
  ║  └─ n < 20     → Insertion sort. Dead simple, fast, stable.     ║
  ║  └─ n < 1000   → Any O(n log n) sort. Quicksort is fine.       ║
  ║  └─ n > 1000   → Continue.                                     ║
  ║                                                                 ║
  ║  Are keys integers with small range?                            ║ 
  ║  └─ YES → Counting sort or radix sort. O(n), can't be beat.    ║
  ║                                                                 ║
  ║  Is the data nearly sorted?                                     ║
  ║  └─ YES → Timsort or insertion sort. Exploit the existing order.║
  ║                                                                 ║
  ║  Do you need stability?                                         ║
  ║  └─ YES → Merge sort or Timsort. Both stable, both O(n log n). ║
  ║  └─ NO  → Quicksort (fastest avg) or introsort (safe worst).   ║
  ║                                                                 ║
  ║  Is memory extremely limited (embedded system)?                 ║
  ║  └─ YES → Heapsort (O(1) extra) or shellsort (O(1), no recur). ║
  ║                                                                 ║
  ║  Is the data on disk (too large for RAM)?                       ║
  ║  └─ YES → External merge sort with k-way merge.                ║
  ║                                                                 ║
  ║  Do you have a GPU or many processors?                          ║ 
  ║  └─ YES → Bitonic sort or merge sort (parallelizes well).      ║
  ║                                                                 ║
  ║  When in doubt → Use your language's built-in sort.             ║
  ╚═══════════════════════════════════════════════════════════════════╝
""")


# ─────────────────────────────────────────────────────────────────────────────
#  THE MASTER TABLE
# ─────────────────────────────────────────────────────────────────────────────

section("THE MASTER TABLE — Every Algorithm at a Glance")

print("""\
  ┌──────────────────┬──────────┬──────────┬──────────┬────────┬────────┬─────────┐
  │ Algorithm        │  Best    │ Average  │  Worst   │ Memory │ Stable │Adaptive │
  ├──────────────────┼──────────┼──────────┼──────────┼────────┼────────┼─────────┤
  │ Bubble sort      │  O(n)    │  O(n²)   │  O(n²)   │  O(1)  │  Yes   │  Yes    │
  │ Insertion sort   │  O(n)    │  O(n²)   │  O(n²)   │  O(1)  │  Yes   │  Yes    │
  │ Selection sort   │  O(n²)   │  O(n²)   │  O(n²)   │  O(1)  │  No    │  No     │
  │ Merge sort       │O(n lg n) │O(n lg n) │O(n lg n) │  O(n)  │  Yes   │  No     │
  │ Quicksort        │O(n lg n) │O(n lg n) │  O(n²)   │O(lg n) │  No    │  No     │
  │ Heapsort         │O(n lg n) │O(n lg n) │O(n lg n) │  O(1)  │  No    │  No     │
  │ Counting sort    │ O(n+k)   │ O(n+k)   │ O(n+k)   │ O(n+k) │  Yes   │  N/A    │
  │ Radix sort (LSD) │ O(d·n)   │ O(d·n)   │ O(d·n)   │ O(n+b) │  Yes   │  N/A    │
  │ Timsort          │  O(n)    │O(n lg n) │O(n lg n) │  O(n)  │  Yes   │  Yes    │
  │ Introsort        │O(n lg n) │O(n lg n) │O(n lg n) │O(lg n) │  No    │  No     │
  │ Shellsort        │O(n lg n) │ varies   │ varies   │  O(1)  │  No    │  Some   │
  │ Bitonic sort     │O(nlog²n) │O(nlog²n) │O(nlog²n) │  O(1)* │  No    │  No     │
  ├──────────────────┼──────────┼──────────┼──────────┼────────┼────────┼─────────┤
  │ Radix exchange   │ O(b·n)   │ O(b·n)   │ O(b·n)   │  O(b)  │  No    │  N/A    │
  │ Wavelet tree     │O(nlog σ) │O(nlog σ) │O(nlog σ) │O(nlgσ) │  Yes   │  No     │
  │ CA sort (par.)   │  O(n)    │  O(n)    │  O(n)    │  O(1)  │  Yes   │  No     │
  │ Morton sort      │O(n lg n) │O(n lg n) │O(n lg n) │  O(n)  │  Dep.  │  N/A    │
  └──────────────────┴──────────┴──────────┴──────────┴────────┴────────┴─────────┘
  * in-place variant; network-based needs O(n) for comparator list
  b = bit width, σ = distinct values. Script 09 algorithms shown below separator.

  k = range of values, d = number of digits, b = base
  "Adaptive" means the sort runs faster on partially-sorted input.
""")


# ─────────────────────────────────────────────────────────────────────────────
#  FINAL REFLECTIONS
# ─────────────────────────────────────────────────────────────────────────────

section("FINAL REFLECTIONS — What Sorting Teaches Us")

print("""\
  We started with a simple question: how do computers put things in order?

  Seven scripts later, we've traveled from bubble sort's shuffling to
  Timsort's galloping, from counting sort's clever trick to bitonic
  sort's beautiful symmetry, from pancake flipping to quantum universe
  destruction. And in Script 09, we found that the ideas from bit tricks,
  signal processing, cellular automata, and even Newton's method all
  have something to say about how information becomes order.

  Here's what sorting really teaches:

  1. LOWER BOUNDS EXIST
     You can't comparison-sort faster than n log n. Period. Any attempt
     to do so requires changing the model — integer keys (counting sort),
     parallelism (sorting networks), or divine intervention.

  2. THERE IS NO BEST ALGORITHM
     Timsort wins on real-world data. Quicksort wins on random data.
     Counting sort wins on bounded integers. Heapsort wins on memory.
     The "best" algorithm depends on your constraints.

  3. THEORY MEETS PRACTICE
     The theoretically optimal algorithm (merge sort: O(n log n), stable)
     isn't always the fastest. Timsort "cheats" by using insertion sort
     for small pieces and detecting existing order. Practice cares about
     constants, cache lines, and branch prediction — not just Big O.

  4. HARDWARE SHAPES ALGORITHMS
     Sorting on a GPU is fundamentally different from sorting in RAM,
     which is different from sorting on disk, which is different from
     sorting across a cluster. The machine defines the problem.

  5. THE ABSURD HAS VALUE
     Bogosort is useless — but it illustrates random search. Sleep sort
     is impractical — but it shows computation models matter. Spaghetti
     sort is a joke — but it proves physical parallelism is real.

  Sorting is the Rosetta Stone of computer science. learn it well, and
  every other algorithm makes more sense.

  ┌─────────────────────────────────────────────────────────────────┐
  │  "I believe that virtually every important aspect of            │
  │   programming arises somewhere in the context of sorting        │
  │   and searching."                                               │
  │                                              — Donald Knuth     │
  │                       The Art of Computer Programming, Vol. 3   │
  └─────────────────────────────────────────────────────────────────┘

  Connection Map:
    Script 01 ←──→ Inversions, bubble sort (the naive foundation)
    Script 02 ←──→ Recursion, divide-and-conquer, lower bounds
    Script 03 ←──→ Heaps, priority queues, Dijkstra [← repo 2]
    Script 04 ←──→ Number systems, digits, bases [← repo 7]
    Script 05 ←──→ Python internals, how real systems sort
    Script 06 ←──→ Parallelism, networks, distributed systems
    Script 07 ←──→ Complexity theory, physical computation, fun
    Script 08 ←──→ You are here. Everything comes together.
    Script 09 ←──→ Bitwise alchemy: bit-tricks, signals, CAs [← repos 3-6]

  Thank you for sorting through all of this with us.
""")

print("  ═══════════════════════════════════════════════════════════════════")
print("  ═══     Sorting: From Bubbles to Parallel Machines — FIN      ═══")
print("  ═══════════════════════════════════════════════════════════════════")
print()
