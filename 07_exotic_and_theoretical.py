#!/usr/bin/env python3
"""
07_exotic_and_theoretical.py — The Wild Ones

Not every sorting algorithm was born to be efficient. Some were born to be
weird. Some to illustrate a point. Some emerged from fever dreams, bar bets,
or the terrifying question: "what if we just shuffled until it's sorted?"

This script is the fun one. We explore algorithms that range from comedic
to profound — from bogosort (the universe's laziest algorithm) to pancake
sorting (the subject of Bill Gates' first published paper).

WARNING: Some of these algorithms are intentionally terrible. Do not deploy
bogosort in production. (We shouldn't have to say this. We're saying it.)

Topics: Bogosort · sleep sort · spaghetti sort · pancake sorting ·
        gravity/bead sort · gnome sort · stooge sort · Stalin sort ·
        intelligent design sort · quantum bogosort · the library sort
"""

import random
import time
import math
import threading

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


# ─────────────────────────────────────────────────────────────────────────────
#  BOGOSORT — The Monkey Shakespeare of Sorting
# ─────────────────────────────────────────────────────────────────────────────

section("BOGOSORT — Hope as a Strategy")

print("""\
  Algorithm:
    1. Is the array sorted?
    2. No? Shuffle it randomly.
    3. Go to step 1.

  That's it. That's the algorithm.

  Expected time complexity: O(n · n!)
  Best case:  O(n)        — it was already sorted, we just checked
  Worst case: O(∞)        — it's randomized, no upper bound guaranteed

  For n = 10:   expected ~36,288,000 comparisons
  For n = 13:   expected ~80,951,270,400 comparisons
  For n = 20:   the heat death of the universe arrives first

  It has one redeeming quality: it uses O(1) extra memory.

  Let's watch it struggle:
""")


def bogosort(arr, max_attempts=10_000_000):
    """Bogosort: shuffle until sorted."""
    arr = arr[:]
    attempts = 0
    while not is_sorted(arr):
        random.shuffle(arr)
        attempts += 1
        if attempts >= max_attempts:
            return arr, attempts, False
    return arr, attempts, True


# Run on tiny arrays and show the agony
random.seed(42)
for n in range(2, 9):
    data = list(range(n, 0, -1))  # worst case: reversed
    t0 = time.perf_counter()
    result, attempts, success = bogosort(data, max_attempts=2_000_000)
    elapsed = time.perf_counter() - t0

    expected = math.factorial(n)
    status = f"✓ in {attempts:,} shuffles" if success else f"✗ gave up after {attempts:,}"
    print(f"  n={n}: {status:>35s}  (expected: {expected:>10,})  [{elapsed:.3f}s]")

print()
print("  Notice how n=8 might already take thousands of shuffles.")
print("  n=9 would take tens of thousands. n=12 would take... don't.")
print()

subsection("Bogosort Enrichment: The Bogosort Family Tree")

print("""\
  Bogosort has spawned a family of intentionally awful algorithms:

  • Bogobogosort: Bogosort the first element. Then bogosort the first two.
    Then the first three. If at any point it's not sorted, START OVER.
    Complexity analysis abandoned by its creator.

  • Bozosort: Like bogosort, but instead of shuffling everything, swap
    just TWO random elements. Then check. Somehow even worse in practice.

  • Worstsort: Uses bogosort as a subroutine. For each comparison, it
    generates all permutations of a subset... to decide how to compare.
    Deliberately designed to be as slow as possible while still terminating.

  • Slowsort (see below): "Multiply and surrender."
""")


# ─────────────────────────────────────────────────────────────────────────────
#  SLOWSORT — Multiply and Surrender
# ─────────────────────────────────────────────────────────────────────────────

section("SLOWSORT — The Anti-Algorithm")

print("""\
  Invented by Broder and Stolfi (1984) as a deliberate parody of divide-
  and-conquer. Instead of "divide and conquer," it's "multiply and
  surrender."

  Algorithm:
    1. Recursively sort the first half
    2. Recursively sort the second half
    3. Compare the last elements of each half — the larger one is the
       overall maximum. Put it at the end.
    4. Recursively sort everything EXCEPT the last element.

  Step 4 is the killer. Instead of solving a smaller problem efficiently,
  it re-sorts nearly the entire array. The recursion goes wider, not deeper.

  Complexity: Ω(n^(log n)) — that's SUPER-POLYNOMIAL.
  It's worse than any polynomial, but not quite exponential.
  It's... maximally pessimal.
""")


def slowsort(arr, lo=0, hi=None):
    """Slowsort: multiply and surrender."""
    if hi is None:
        arr = arr[:]
        hi = len(arr) - 1
        slowsort(arr, lo, hi)
        return arr

    if lo >= hi:
        return

    mid = (lo + hi) // 2
    slowsort(arr, lo, mid)       # sort first half
    slowsort(arr, mid + 1, hi)   # sort second half

    # The maximum of the two halves' maxima is the overall max
    if arr[mid] > arr[hi]:
        arr[mid], arr[hi] = arr[hi], arr[mid]

    # Now sort everything EXCEPT the confirmed maximum
    slowsort(arr, lo, hi - 1)    # <-- this is the "surrender" part


# Demo on tiny array (it's REALLY slow for n > ~15)
demo = [5, 3, 8, 1, 7, 2, 6, 4]
result = slowsort(demo)
print(f"  Input:  {demo}")
print(f"  Output: {result}")
print(f"  Correct: {result == sorted(demo)} ✓")
print()

print("  Timing slowsort for increasing n:")
print()
for n in range(4, 17, 2):
    data = list(range(n, 0, -1))
    t0 = time.perf_counter()
    slowsort(data)
    elapsed = time.perf_counter() - t0
    bar = "█" * min(int(elapsed * 200), 50)
    print(f"    n={n:>2d}: {elapsed:>8.4f}s  {bar}")
    if elapsed > 5:
        print("    (stopping here — it only gets worse)")
        break

print()


# ─────────────────────────────────────────────────────────────────────────────
#  SLEEP SORT — Time as a Sorting Mechanism
# ─────────────────────────────────────────────────────────────────────────────

section("SLEEP SORT — Let Time Sort It Out")

print("""\
  Posted anonymously on 4chan's /prog/ board in 2011. Genuinely novel.

  Algorithm:
    For each element x in the array:
      spawn a thread that sleeps for x * scale seconds, then prints x.

  The smallest values wake up first. Output arrives in sorted order.

  Problems:
    • Time complexity: O(max(array)) — time depends on VALUES, not count
    • Race conditions on very close values (threads may wake out of order)
    • Negative numbers don't work (can't sleep negative seconds)
    • Absurdly slow on large values

  But it's genuinely O(1) comparisons. Zero comparisons, in fact.
  The operating system's thread scheduler IS the sorting algorithm.

  Let's simulate it:
""")


def sleep_sort(arr, scale=0.002):
    """Sleep sort: threads sleep proportional to value, output in order."""
    result = []
    lock = threading.Lock()
    threads = []

    def worker(val):
        time.sleep(val * scale)
        with lock:
            result.append(val)

    for val in arr:
        t = threading.Thread(target=worker, args=(val,))
        threads.append(t)

    # Start all threads simultaneously
    for t in threads:
        t.start()

    # Wait for all to finish
    for t in threads:
        t.join()

    return result


# Demo with small values well spread apart
demo = [5, 3, 8, 1, 9, 2, 7, 4, 6]
print(f"  Input:    {demo}")
t0 = time.perf_counter()
result = sleep_sort(demo, scale=0.01)
elapsed = time.perf_counter() - t0
print(f"  Output:   {result}")
print(f"  Correct:  {result == sorted(demo)} {'✓' if result == sorted(demo) else '(race condition!)'}")
print(f"  Time:     {elapsed:.3f}s (limited by max value × scale)")
print()

# Show the timing dependence
print("  Time depends on max VALUE, not array SIZE:")
for mx in [10, 50, 100, 500]:
    data = random.sample(range(1, mx + 1), min(20, mx))
    t0 = time.perf_counter()
    sleep_sort(data, scale=0.001)
    elapsed = time.perf_counter() - t0
    print(f"    max={mx:>4d}, n={len(data):>2d}: {elapsed:.3f}s")

print()


# ─────────────────────────────────────────────────────────────────────────────
#  SPAGHETTI SORT — Physical Computing
# ─────────────────────────────────────────────────────────────────────────────

section("SPAGHETTI SORT — The Analog Computer")

print("""\
  Take a handful of spaghetti, each piece cut to the length of one value.
  Hold them in a bundle. Slam the bundle on the table so all bottoms align.
  The tallest piece sticks up the most. Pull it out. That's the maximum.
  Repeat.

  This is GENUINE O(n) sorting — in the physical world. Each piece finds
  its position simultaneously by gravity. The "comparison" is done by
  physics in parallel.

  Of course, digitally simulating this gives us... just a normal sort.
  The point is conceptual: some problems that are O(n log n) digitally
  become O(n) with the right physical substrate.

  Simulating spaghetti sort:
""")


def spaghetti_sort(arr):
    """Spaghetti sort simulation: repeatedly find and remove the max."""
    result = []
    remaining = arr[:]

    while remaining:
        # "Slam on table" — find the tallest piece
        max_val = max(remaining)
        remaining.remove(max_val)
        result.append(max_val)

    result.reverse()  # We extracted max-first, so reverse for ascending
    return result


demo = [7, 3, 9, 1, 5, 8, 2, 6, 4]
print(f"  Input:  {demo}")

print("  *slams spaghetti on table*")
print()

result = spaghetti_sort(demo)
for i, val in enumerate(result):
    rod = "│" * val
    print(f"    Pull #{i+1}: {rod} ({val})")

print(f"\n  Output: {result}")
print(f"  Correct: {result == sorted(demo)} ✓")
print()
print("  In the physical world: O(n). In simulation: O(n²) because max() is O(n).")
print("  The universe is a better computer than we are, sometimes.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  PANCAKE SORTING — Bill Gates' First Paper
# ─────────────────────────────────────────────────────────────────────────────

section("PANCAKE SORTING — Bill Gates' First Paper")

print("""\
  1979. Before Microsoft. Bill Gates co-authored a paper with Christos
  Papadimitriou on "Bounds for Sorting by Prefix Reversals."

  The problem: you have a stack of pancakes of different sizes. The ONLY
  operation allowed is to insert a spatula at any position and FLIP all
  pancakes above it.

  This is prefix reversal: reverse the first k elements.

    [3, 1, 4, 2]
     flip(3) → [4, 1, 3, 2]    (reverse first 3)
     flip(4) → [2, 3, 1, 4]    (reverse all 4)
     flip(2) → [3, 2, 1, 4]    (reverse first 2)
     flip(3) → [1, 2, 3, 4]    (reverse first 3) ✓ sorted!

  Gates and Papadimitriou proved:
    • Any stack of n pancakes can be sorted in at most (5n + 5) / 3 flips
    • The worst case requires at least 15n/14 flips

  The EXACT answer for general n is STILL UNKNOWN. (Yes, really.)

  The "burnt pancake problem" adds a twist: each pancake has a burnt side,
  and you must end with all burnt sides down.

  Connection to biology: sorting by reversals models chromosome mutations
  in computational genomics. Evolution "sorts" genes through reversals.
""")


def pancake_sort(arr):
    """Pancake sort: only flip (prefix reversal) operations."""
    arr = arr[:]
    n = len(arr)
    flips = []

    for size in range(n, 1, -1):
        # Find the largest pancake in arr[:size]
        max_idx = arr.index(max(arr[:size]))

        if max_idx == size - 1:
            continue  # Already in position

        if max_idx != 0:
            # Flip it to the top
            arr[:max_idx + 1] = arr[:max_idx + 1][::-1]
            flips.append(max_idx + 1)

        # Flip it to its correct position
        arr[:size] = arr[:size][::-1]
        flips.append(size)

    return arr, flips


demo = [3, 1, 5, 2, 4]
print(f"  Input: {demo}")
print()

arr = demo[:]
result, flips = pancake_sort(demo)

# Replay flips with visualization
arr = demo[:]
print(f"  {'Step':>6s}  {'Flip':>6s}  {'Array':>25s}  {'Action'}")
print(f"  {'─'*6}  {'─'*6}  {'─'*25}  {'─'*30}")
print(f"  {'start':>6s}  {'':>6s}  {str(arr):>25s}")

for i, flip in enumerate(flips):
    arr[:flip] = arr[:flip][::-1]
    print(f"  {i+1:>6d}  {flip:>6d}  {str(arr):>25s}  reverse first {flip} elements")

print(f"\n  Sorted in {len(flips)} flips (upper bound: {(5 * len(demo) + 5) // 3})")
print()

# Stats on random arrays
print("  Flip counts for random arrays:")
for n in range(5, 21, 3):
    random.seed(42)
    total_flips = 0
    trials = 100
    for _ in range(trials):
        data = random.sample(range(1, n + 1), n)
        _, flips = pancake_sort(data)
        total_flips += len(flips)
    avg = total_flips / trials
    bound = (5 * n + 5) / 3
    print(f"    n={n:>2d}: avg {avg:>5.1f} flips  (Gates-Papadimitriou bound: {bound:.0f})")

print()


# ─────────────────────────────────────────────────────────────────────────────
#  GNOME SORT — The Garden Gnome's Method
# ─────────────────────────────────────────────────────────────────────────────

section("GNOME SORT — Sorting Like a Garden Gnome")

print("""\
  Hamid Sarbazi-Azad, 2000. Also called "stupid sort."

  Imagine a garden gnome sorting flower pots. He looks at the two pots
  next to him. If they're in order, he steps right. If not, he swaps them
  and steps left. When he reaches the right end, he's done.

  It's basically insertion sort without the inner loop index — the gnome
  just walks back and forth. Same O(n²), but only ONE comparison per step.
  The simplest possible sort that's simpler than even bubble sort.
""")


def gnome_sort(arr):
    """Gnome sort: swap and step."""
    arr = arr[:]
    n = len(arr)
    pos = 0
    steps = 0

    while pos < n:
        if pos == 0 or arr[pos] >= arr[pos - 1]:
            pos += 1
        else:
            arr[pos], arr[pos - 1] = arr[pos - 1], arr[pos]
            pos -= 1
        steps += 1

    return arr, steps


demo = [5, 3, 8, 1, 4]
arr = demo[:]
print(f"  Input: {demo}")
print()

# Trace the gnome's journey
pos = 0
step = 0
print(f"  {'Step':>6s}  {'Pos':>4s}  {'Action':>12s}  {'Array':>25s}  {'Gnome'}")
print(f"  {'─'*6}  {'─'*4}  {'─'*12}  {'─'*25}  {'─'*20}")

arr = demo[:]
pos = 0
for step in range(40):
    gnome_pos = "  " * pos + "🌻"
    if pos >= len(arr):
        print(f"  {step:>6d}  {pos:>4d}  {'done':>12s}  {str(arr):>25s}  {gnome_pos}")
        break
    if pos == 0 or arr[pos] >= arr[pos - 1]:
        action = "step right"
        print(f"  {step:>6d}  {pos:>4d}  {action:>12s}  {str(arr):>25s}  {gnome_pos}")
        pos += 1
    else:
        arr[pos], arr[pos - 1] = arr[pos - 1], arr[pos]
        action = "swap & left"
        print(f"  {step:>6d}  {pos:>4d}  {action:>12s}  {str(arr):>25s}  {gnome_pos}")
        pos -= 1

result, steps = gnome_sort(demo)
print(f"\n  Sorted in {steps} steps. Output: {result}")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  STOOGE SORT — The Three Stooges of Sorting
# ─────────────────────────────────────────────────────────────────────────────

section("STOOGE SORT — The Three Stooges")

print("""\
  Algorithm:
    1. If the first element > the last element, swap them.
    2. If there are 3+ elements:
       a. Stooge-sort the first 2/3
       b. Stooge-sort the last 2/3
       c. Stooge-sort the first 2/3 again

  Why three times? Because after sorting the first 2/3 and the last 2/3,
  some elements from the "no man's land" in the middle might be wrong.
  The third pass fixes them.

  Time complexity: O(n^(log 3 / log 1.5)) = O(n^2.709...)

  That's WORSE than O(n²). Stooge sort is slower than bubble sort.
  It's not good at anything. It's just... stooge-y.
""")


def stooge_sort(arr, lo=0, hi=None, depth=0):
    """Stooge sort: sort 2/3, sort 2/3, sort 2/3."""
    if hi is None:
        arr = arr[:]
        hi = len(arr) - 1
        stooge_sort(arr, lo, hi)
        return arr

    if arr[lo] > arr[hi]:
        arr[lo], arr[hi] = arr[hi], arr[lo]

    if hi - lo + 1 > 2:
        third = (hi - lo + 1) // 3
        stooge_sort(arr, lo, hi - third, depth + 1)
        stooge_sort(arr, lo + third, hi, depth + 1)
        stooge_sort(arr, lo, hi - third, depth + 1)


demo = [5, 3, 8, 1, 7, 2]
result = stooge_sort(demo)
print(f"  Input:  {demo}")
print(f"  Output: {result}")
print(f"  Correct: {result == sorted(demo)} ✓")
print()

print("  Timing stooge sort (it's painful):")
for n in [5, 10, 20, 50, 100]:
    data = list(range(n, 0, -1))
    t0 = time.perf_counter()
    stooge_sort(data)
    elapsed = time.perf_counter() - t0
    bar = "█" * min(int(elapsed * 50), 50)
    print(f"    n={n:>3d}: {elapsed:>8.4f}s  {bar}")
    if elapsed > 5:
        print("    (stopping — the stooges need a break)")
        break

print()


# ─────────────────────────────────────────────────────────────────────────────
#  GRAVITY (BEAD) SORT — Physics as an Algorithm
# ─────────────────────────────────────────────────────────────────────────────

section("GRAVITY (BEAD) SORT — Letting Gravity Do the Work")

print("""\
  Imagine an abacus on its side. Each rod has beads equal to the value.
  Tilt it so beads fall down. They stack up in sorted order.

  Value 5: ●●●●●
  Value 3: ●●●
  Value 7: ●●●●●●●
  Value 1: ●
  Value 4: ●●●●

  After gravity:

  Value 1: ●
  Value 3: ●●●
  Value 4: ●●●●
  Value 5: ●●●●●
  Value 7: ●●●●●●●

  Beads in each column fall to the bottom. The row widths become the
  sorted values. O(1) with physical beads (all fall simultaneously).
  O(n·max) in simulation.
""")


def bead_sort(arr):
    """Bead/gravity sort simulation."""
    if not arr:
        return []
    mx = max(arr)
    n = len(arr)

    # Create the bead grid
    grid = [[0] * mx for _ in range(n)]
    for i, val in enumerate(arr):
        for j in range(val):
            grid[i][j] = 1

    # Let beads fall (column by column)
    for col in range(mx):
        beads = sum(grid[row][col] for row in range(n))
        for row in range(n):
            grid[row][col] = 0
        # Stack beads at the bottom
        for row in range(n - 1, n - 1 - beads, -1):
            grid[row][col] = 1

    # Read off row widths
    return [sum(grid[row]) for row in range(n)]


demo = [5, 3, 7, 1, 4]
print(f"  Input: {demo}\n")

# Visualize the bead grid
mx = max(demo)
print("  Before gravity:")
for i, val in enumerate(demo):
    beads = "●" * val + "·" * (mx - val)
    print(f"    Row {i} ({val}): {beads}")

result = bead_sort(demo)
print(f"\n  After gravity:")
for i, val in enumerate(result):
    beads = "●" * val + "·" * (mx - val)
    print(f"    Row {i} ({val}): {beads}")

print(f"\n  Sorted: {result}")
print(f"  Correct: {result == sorted(demo)} ✓")
print()
print("  Like spaghetti sort: O(1) physically, O(n × max) digitally.")
print("  Only works for non-negative integers.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  STALIN SORT — The Authoritarian Approach
# ─────────────────────────────────────────────────────────────────────────────

section("STALIN SORT — Remove What Doesn't Fit")

print("""\
  Algorithm:
    1. Walk through the array.
    2. If an element is less than the previous one, REMOVE IT.
    3. The remaining elements are sorted.

  Time:    O(n)
  Space:   O(1)
  Stable:  Yes
  Correct: ...technically the output IS sorted

  "The list is now sorted. We've also lost most of our data.
   But that's a sacrifice we're willing to make." — The internet

  Also known as: "dictator sort," "authoritarian sort," "purge sort."
""")


def stalin_sort(arr):
    """Stalin sort: remove elements that are out of order."""
    if not arr:
        return [], []
    result = [arr[0]]
    purged = []

    for i in range(1, len(arr)):
        if arr[i] >= result[-1]:
            result.append(arr[i])
        else:
            purged.append(arr[i])

    return result, purged


demo = [1, 5, 3, 8, 2, 9, 4, 7, 6, 10]
print(f"  Input:   {demo}")

result, purged = stalin_sort(demo)
print(f"  Sorted:  {result}")
print(f"  Purged:  {purged}")
print(f"  Survived: {len(result)}/{len(demo)} elements ({100*len(result)/len(demo):.0f}%)")
print()

# Survival rate for random arrays
print("  Expected survival rate on random data:")
print(f"  (longest increasing subsequence ≈ 2√n for random permutations)\n")
for n in [10, 100, 1000, 10000]:
    random.seed(42)
    data = random.sample(range(n * 10), n)
    result, purged = stalin_sort(data)
    expected_lis = 2 * math.sqrt(n)
    print(f"    n={n:>5d}: survived {len(result):>5d} ({100*len(result)/n:>5.1f}%)  "
          f"expected ~{expected_lis:>6.0f} ({100*expected_lis/n:>5.1f}%)")

print()
print("  The survivor count is approximately the longest increasing subsequence.")
print("  For random data, that's ~2√n. So stalin_sort preserves √n of n elements.")
print("  At n = 1,000,000 you'd keep about 2,000. Efficient? Yes. Useful? Well...")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  INTELLIGENT DESIGN SORT
# ─────────────────────────────────────────────────────────────────────────────

subsection("Intelligent Design Sort")

print("""\
  Algorithm:
    The probability that any given array is in the exact order it's in
    by chance is 1/n!. For even modest n, this is astronomically unlikely.
    Therefore, some intelligent agent must have deliberately arranged the
    elements in this order — and who are we to question that?

    The array is already sorted by divine decree.

  Time:    O(1)
  Space:   O(1)
  Correct: By faith

  (This is a real joke algorithm from the Uncyclopedia.)
""")


def intelligent_design_sort(arr):
    """The array is already optimally arranged."""
    return arr  # It is as it should be


# ─────────────────────────────────────────────────────────────────────────────
#  QUANTUM BOGOSORT
# ─────────────────────────────────────────────────────────────────────────────

subsection("Quantum Bogosort")

print("""\
  A thought experiment using the many-worlds interpretation of quantum
  mechanics:

    1. Randomly shuffle the array.
    2. If the array is not sorted, destroy the universe.
    3. The surviving universe contains the sorted array.

  By the many-worlds interpretation, ALL possible shuffles occur
  simultaneously in parallel universes. The only universe that survives
  is the one where the shuffle happened to produce a sorted array.

  From the perspective of the observer: O(n) — you just check once.
  From the perspective of the multiverse: O(n!) dead universes.

  Prerequisites: quantum computer, many-worlds interpretation, willingness
  to destroy 99.99999...% of reality.

  Side effects: mild existential dread.
""")


# ─────────────────────────────────────────────────────────────────────────────
#  MIRACLE SORT
# ─────────────────────────────────────────────────────────────────────────────

subsection("Miracle Sort")

print("""\
  Algorithm:
    1. Check if the array is sorted.
    2. If not, wait. Maybe cosmic rays will flip the right bits in memory.
    3. Go to step 1.

  Expected time: slightly longer than the heat death of the universe.
  But TECHNICALLY it could work at any moment.

  This is an actual O(1) best case with... undefined average case.
""")


# ─────────────────────────────────────────────────────────────────────────────
#  CYCLE SORT
# ─────────────────────────────────────────────────────────────────────────────

subsection("Cycle Sort")

print("""\
  Cycle sort is the mathematically OPTIMAL sort for minimizing writes.
  Every element is written AT MOST once to its correct position.

  Why does that matter?
  • Flash memory (SSDs, USB drives) has a limited number of write cycles
  • EEPROM can wear out after ~100,000 writes per cell
  • If writes are expensive and reads are cheap, cycle sort wins

  The idea: for each element, COUNT how many elements are smaller than it.
  That count IS the element's correct index. Then follow the cycle of
  displacements until every element is home.

  Time: O(n²) — not fast, but only O(n) writes (provably optimal).
""")


def cycle_sort(arr, trace=False):
    """In-place cycle sort. Returns (sorted_array, writes)."""
    arr = arr[:]
    n = len(arr)
    writes = 0

    for cycle_start in range(n - 1):
        item = arr[cycle_start]

        # Find position: count elements smaller than item
        pos = cycle_start
        for i in range(cycle_start + 1, n):
            if arr[i] < item:
                pos += 1

        # Already in correct position
        if pos == cycle_start:
            continue

        # Skip duplicates
        while item == arr[pos]:
            pos += 1

        # Place at correct position
        arr[pos], item = item, arr[pos]
        writes += 1

        # Follow the cycle
        while pos != cycle_start:
            pos = cycle_start
            for i in range(cycle_start + 1, n):
                if arr[i] < item:
                    pos += 1
            while item == arr[pos]:
                pos += 1
            arr[pos], item = item, arr[pos]
            writes += 1

    return arr, writes


# Demo
demo = [4, 1, 3, 1, 5, 2, 5, 3]
result, w = cycle_sort(demo, trace=True)
print(f"  Input:   {demo}")
print(f"  Output:  {result}")
print(f"  Writes:  {w} (out of {len(demo)} elements)")
print()

# Compare writes
sizes = [50, 100, 200]
print(f"  {'n':>6s}  {'Cycle writes':>14s}  {'n (theoretical)':>16s}  {'Ratio':>8s}")
print(f"  {'─'*6}  {'─'*14}  {'─'*16}  {'─'*8}")
for sz in sizes:
    random.seed(42)
    data = random.sample(range(sz * 10), sz)
    _, wr = cycle_sort(data)
    print(f"  {sz:>6d}  {wr:>14d}  {sz:>16d}  {wr/sz:>7.2f}×")

print()
print("  Cycle sort typically does fewer writes than n — it's the MINIMUM")
print("  possible. If you have flash memory and can afford O(n²) reads,")
print("  this is your algorithm.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  PATIENCE SORT
# ─────────────────────────────────────────────────────────────────────────────

subsection("Patience Sort")

print("""\
  Named after the card game "Patience" (Solitaire), this algorithm sorts
  by dealing elements into piles, then merging the piles.

  DEALING RULES:
    • Look at the element
    • Place it on the leftmost pile whose top is >= the element
    • If no such pile exists, create a new pile

  The KEY insight: the NUMBER OF PILES equals the length of the
  Longest Increasing Subsequence (LIS) of the input.

  This connects to the Erdős–Szekeres theorem (1935): any sequence of
  more than (r-1)(s-1) distinct numbers contains an increasing subsequence
  of length r OR a decreasing subsequence of length s.

  Time: O(n log n) with binary search for pile placement
  Space: O(n)
""")


import heapq

def patience_sort(arr):
    """Sort using patience/solitaire algorithm. Returns (sorted, num_piles)."""
    if not arr:
        return [], 0

    piles = []  # Each pile is a list (stack); we compare by top element

    for val in arr:
        # Binary search for leftmost pile with top >= val
        lo, hi = 0, len(piles)
        while lo < hi:
            mid = (lo + hi) // 2
            if piles[mid][-1] >= val:
                hi = mid
            else:
                lo = mid + 1

        if lo == len(piles):
            piles.append([val])  # New pile
        else:
            piles[lo].append(val)

    num_piles = len(piles)

    # k-way merge using a min-heap
    # Each heap entry: (value, pile_index)
    heap = []
    for i, pile in enumerate(piles):
        heapq.heappush(heap, (pile.pop(), i))

    result = []
    while heap:
        val, pile_idx = heapq.heappop(heap)
        result.append(val)
        if piles[pile_idx]:
            heapq.heappush(heap, (piles[pile_idx].pop(), pile_idx))

    return result, num_piles


# Demo with visual piles
demo = [7, 2, 8, 1, 3, 9, 4, 6, 5]
print(f"  Input: {demo}")
print()

# Show dealing process
print("  Dealing into piles:")
piles_viz = []
for val in demo:
    placed = False
    for pile in piles_viz:
        if pile[-1] >= val:
            pile.append(val)
            placed = True
            break
    if not placed:
        piles_viz.append([val])
    pile_str = "  ".join(f"[{','.join(str(x) for x in p)}]" for p in piles_viz)
    print(f"    Deal {val}: {pile_str}")

result, n_piles = patience_sort(demo)
print()
print(f"  Number of piles: {n_piles}")
print(f"  → LIS length = {n_piles}")
print(f"  Sorted: {result}")
print()

# LIS connection
print("  THE LIS CONNECTION:")
print("  One longest increasing subsequence in [7,2,8,1,3,9,4,6,5]:")
print("  → [1, 3, 4, 6] or [2, 3, 4, 5] — length 4 = number of piles")
print()
print("  This gives us an O(n log n) algorithm for finding the LENGTH")
print("  of the longest increasing subsequence — a classic DP problem!")
print()


# ═════════════════════════════════════════════════════════════════════════════
#  THE MEMETIC MENAGERIE — Sorts That Exist Because The Internet Does
# ═════════════════════════════════════════════════════════════════════════════

section("THE MEMETIC MENAGERIE — Sorts That Shouldn't Exist (But Do)")

print("""\
  Computer science has a proud tradition of naming algorithms after things
  that have nothing to do with sorting. We now continue that tradition
  with algorithms inspired by astrophysics, middle management, political
  theory, Marvel villains, domestic cats, and temporal paradoxes.

  Each of these is terrible. Each of these teaches something real.
""")


# ─────────────────────────────────────────────────────────────────────────────
#  SOLAR SYSTEM RESONANCE SORT
# ─────────────────────────────────────────────────────────────────────────────

subsection("Solar System Resonance Sort")

print("""\
  In our solar system, planets interact gravitationally — but the REALLY
  interesting stuff happens at orbital resonances: moments when planets'
  periods form integer ratios (Jupiter:Saturn ≈ 5:2, Neptune:Pluto = 3:2).

  Solar System Resonance Sort simulates this cosmic patience:
    • Each array position is a "planet" with an orbital period proportional
      to its index (inner planets orbit faster)
    • A comparison between positions i and j can only occur when their
      orbits align — i.e., when the simulation clock is a multiple of
      lcm(period_i, period_j)
    • When aligned, if the pair is out of order, gravity swaps them

  In essence: bubble sort, but most of the time you're just... WAITING
  for the planets to align. Which is cosmically accurate.

  The deeper lesson: EVENT-DRIVEN computation. The algorithm's work
  depends not on the data but on an external clock. This is how
  interrupt-driven I/O, network polling, and real-time systems work.

  Time: O(n² × max_lcm) — astronomically slow.
""")


def solar_resonance_sort(arr, trace=False):
    """Sort array using planetary alignment events."""
    arr = arr[:]
    n = len(arr)

    # Each position has an orbital period: inner positions orbit faster
    periods = [i + 2 for i in range(n)]  # periods 2, 3, 4, ...

    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a

    def lcm(a, b):
        return a * b // gcd(a, b)

    # Build alignment schedule: for each pair, when do they align?
    events = []
    for i in range(n):
        for j in range(i + 1, n):
            alignment = lcm(periods[i], periods[j])
            events.append((alignment, i, j))

    # Sort events by alignment time (earliest alignments first)
    events.sort()

    # Run the simulation: process events in time order
    clock = 0
    swaps = 0
    alignments_checked = 0
    passes = 0

    while not is_sorted(arr) and passes < 3:
        for alignment_time, i, j in events:
            alignments_checked += 1
            if arr[i] > arr[j]:
                arr[i], arr[j] = arr[j], arr[i]
                swaps += 1
                if trace and swaps <= 8:
                    print(f"    t={alignment_time:>4d}: planets {i} & {j} align → "
                          f"swap! {arr[:min(n,12)]}{'...' if n>12 else ''}")
        passes += 1

    return arr, swaps, alignments_checked


# Demo
demo = [8, 3, 6, 1, 5, 2, 7, 4]
print(f"  Input: {demo}")
print()
print("  Planetary alignment events:")
result, swaps, checks = solar_resonance_sort(demo, trace=True)
print()
print(f"  Output:  {result}")
print(f"  Swaps:   {swaps}")
print(f"  Alignments checked: {checks}")
print(f"  Correct: {'✓' if result == sorted(demo) else '✗'}")
print()
print("  Most of the universe's runtime is spent waiting for alignment.")
print("  Just like most of YOUR computer's time is spent waiting for I/O.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  BUREAUCRACY SORT
# ─────────────────────────────────────────────────────────────────────────────

subsection("Bureaucracy Sort")

print("""\
  In a large corporation, no action can occur without management approval.
  Bureaucracy Sort models this: every swap must be approved by a chain
  of managers. Each manager takes time proportional to their seniority.

  Algorithm:
    1. Find an out-of-order adjacent pair
    2. Submit a swap request to Manager Level 1
    3. Manager 1 approves and escalates to Manager 2
    4. Manager 2 adds it to next week's agenda
    5. Continue up the chain until CEO approves
    6. Perform the swap
    7. File paperwork (increment bureaucracy counter)
    8. Repeat from step 1

  Hidden lesson: this is actually just BUBBLE SORT with O(k) overhead
  per swap, where k is the management chain length. It demonstrates
  how constant factors can dominate — an algorithm that is O(n²) in
  theory can become O(n² × k) when institutional overhead is added.

  This is why your company's deployment pipeline takes 3 weeks.
""")


def bureaucracy_sort(arr, management_depth=5, trace=False):
    """Bubble sort with bureaucratic overhead per swap."""
    arr = arr[:]
    n = len(arr)
    forms_filed = 0
    approvals = 0
    swaps = 0
    meetings = 0
    memos = []

    titles = ["Team Lead", "Manager", "Senior Manager", "VP", "SVP", "CEO"]
    titles = titles[:management_depth]

    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                # Begin approval chain
                request_id = f"SWAP-{forms_filed + 1:04d}"

                for level, title in enumerate(titles):
                    approvals += 1
                    # Each manager "reviews" (does nothing useful)
                    meetings += 1

                # Swap approved!
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1
                forms_filed += 1

                if trace and swaps <= 5:
                    chain_str = " → ".join(titles)
                    print(f"    {request_id}: swap [{j}]↔[{j+1}] "
                          f"approved by {chain_str}")

    memo = (f"  Total requests filed: {forms_filed}, approvals: {approvals}, "
            f"meetings: {meetings}")

    return arr, forms_filed, approvals, meetings


# Demo
demo = [5, 3, 4, 1, 2]
print(f"  Input: {demo}")
print()
print("  Approval chain (depth = 5):")
result, forms, approvals, meetings = bureaucracy_sort(demo, 5, trace=True)
print(f"    ... ({forms - 5} more swap requests processed)")
print()
print(f"  Output:     {result}")
print(f"  Forms:      {forms}")
print(f"  Approvals:  {approvals}")
print(f"  Meetings:   {meetings}")
print(f"  Overhead:   {approvals / max(forms, 1):.0f} approvals per actual swap")
print()
print("  Same result as bubble sort. 5× the meetings.")
print("  Now you know why enterprise software is slow.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  DEMOCRACY SORT
# ─────────────────────────────────────────────────────────────────────────────

subsection("Democracy Sort")

print("""\
  In a democracy, positions are determined by popular vote.
  Democracy Sort lets the elements VOTE on who should go first.

  For each position i, every element casts a vote:
    "I believe the element at index k should go in position i"
  The winner (by plurality) gets placed.

  Algorithm:
    1. For position 0: every element votes for who should be smallest
       (each element votes for the element it thinks is smallest)
    2. The element with the most votes goes to position 0
    3. Repeat for remaining positions
    4. Ties are broken by seniority (original index)

  This is secretly a SELECTION SORT wearing a democratic costume —
  the "vote" each element casts is just a comparison. But the framing
  reveals something: sorting IS consensus. The sorted order is the
  one arrangement all elements "agree" on.

  Time: O(n²) — democracy is not efficient, but it's legitimate.
""")


def democracy_sort(arr, trace=False):
    """Selection sort disguised as an election."""
    arr = arr[:]
    n = len(arr)
    placed = [False] * n
    result = []
    elections = 0
    total_votes = 0

    for position in range(n):
        # Each unplaced element gets votes from all unplaced elements
        # An element j "votes for" the element it considers smallest
        candidates = [i for i in range(n) if not placed[i]]
        votes = {c: 0 for c in candidates}

        for voter in candidates:
            # Each voter votes for the smallest element they can see
            best = voter
            for c in candidates:
                total_votes += 1
                if arr[c] < arr[best]:
                    best = c
            votes[best] += 1

        # Winner: most votes (ties broken by value, then index)
        winner = max(candidates, key=lambda c: (votes[c], -arr[c], -c))
        result.append(arr[winner])
        placed[winner] = True
        elections += 1

        if trace and elections <= 4:
            vote_str = ", ".join(f"{arr[c]}:{votes[c]}v" for c in candidates[:6])
            print(f"    Election {elections}: candidates vote → "
                  f"{vote_str}{'...' if len(candidates) > 6 else ''} "
                  f"→ winner: {arr[winner]}")

    return result, elections, total_votes


# Demo
demo = [7, 2, 5, 1, 9, 3]
print(f"  Input: {demo}")
print()
print("  Elections:")
result, elections, votes = democracy_sort(demo, trace=True)
print(f"    ... ({elections - 4} more elections held)")
print()
print(f"  Output:     {result}")
print(f"  Elections:  {elections}")
print(f"  Total votes cast: {votes}")
print(f"  Correct: {'✓' if result == sorted(demo) else '✗'}")
print()
print("  Democracy: slow, expensive, but always gets the right answer.")
print("  (If only real elections were this reliable.)")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  THANOS SORT
# ─────────────────────────────────────────────────────────────────────────────

subsection("Thanos Sort")

print("""\
  "Perfectly balanced, as all things should be."

  Like Stalin Sort, Thanos Sort achieves order through elimination.
  But Thanos is FAIR — he snaps away exactly HALF the array at random.
  Then checks if the survivors are sorted. If not... another snap.

  Algorithm:
    1. Check if array is sorted.
    2. If not, randomly remove half the elements.
    3. Repeat until sorted (or nothing remains).

  The expected number of survivors after k snaps: n / 2^k
  The array is guaranteed to be sorted when ≤ 1 element remains.

  Unlike Stalin Sort (which is biased — it keeps a specific subsequence),
  Thanos Sort is genuinely random. Sometimes it accidentally preserves
  a long sorted subsequence. Sometimes it doesn't.

  Time: O(n) per snap × O(log n) snaps expected
  Correctness: ✗ (lossy — the output is sorted, but data is lost)
  Fairness: perfectly balanced.
""")


def thanos_sort(arr, trace=False):
    """Snap away half the array until sorted."""
    arr = arr[:]
    snaps = 0
    casualties = 0
    history = [len(arr)]

    while len(arr) > 1 and not is_sorted(arr):
        half = max(1, len(arr) // 2)
        random.shuffle(arr)
        removed = arr[half:]
        arr = arr[:half]
        arr_sorted_check = arr  # we'll re-check next iteration
        casualties += len(removed)
        snaps += 1
        history.append(len(arr))
        if trace:
            survivors = arr[:8]
            print(f"    Snap {snaps}: {len(removed)} eliminated → "
                  f"{len(arr)} survive {survivors}{'...' if len(arr) > 8 else ''}")

    # Sort survivors (Thanos is merciful to the last few)
    arr.sort()

    return arr, snaps, casualties, history


# Demo
random.seed(42)
demo = list(range(1, 33))
random.shuffle(demo)
print(f"  Input: {demo[:12]}... ({len(demo)} elements)")
print()
print("  *snap*")
random.seed(42)
result, snaps, dead, hist = thanos_sort(demo, trace=True)
print()
print(f"  Survivors: {result}")
print(f"  Snaps:     {snaps}")
print(f"  Casualties: {dead} of {len(demo)} ({dead/len(demo)*100:.0f}%)")
print(f"  Population: {' → '.join(str(h) for h in hist)}")
print()
print("  The hardest choices require the strongest wills.")
print("  Also: this is a metaphor for random sampling in statistics.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  CAT SORT
# ─────────────────────────────────────────────────────────────────────────────

subsection("Cat Sort")

print("""\
  Anyone who has owned a cat knows: cats are nondeterministic.
  Cat Sort models the behavior of a cat tasked with sorting:

  At each step, the cat does one of the following (randomly):
    30%  — Compare two adjacent elements, swap if needed (productive!)
    15%  — Knock an element off the table (remove a random element)
    25%  — Stare at the array and do nothing
    20%  — Bat an element to a random position (random swap)
    10%  — Take a nap (skip several iterations)

  Cat Sort terminates when:
    a) The array is sorted (unlikely)
    b) The cat gets bored (iteration limit reached)
    c) All elements have been knocked off the table

  Hidden lesson: NONDETERMINISTIC AUTOMATA. A machine that chooses
  randomly between actions at each step. The "productive" path exists
  (30% swaps), but the cat might never take it consistently.

  Expected time: O(is_the_cat_in_the_mood)
""")


def cat_sort(arr, max_steps=500, trace=False):
    """Simulate a cat's attempt at sorting."""
    arr = arr[:]
    n = len(arr)
    step = 0
    productive_swaps = 0
    stares = 0
    knocked_off = 0
    random_bats = 0
    naps = 0
    events = []

    while step < max_steps and len(arr) > 1:
        action = random.random()
        step += 1

        if action < 0.30 and len(arr) > 1:
            # Productive: compare & swap adjacent
            i = random.randint(0, len(arr) - 2)
            if arr[i] > arr[i + 1]:
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
                productive_swaps += 1
                if trace and len(events) < 6:
                    events.append(f"    Step {step:>3d}: 🐱 Compare & swap [{i}]↔[{i+1}]")

        elif action < 0.45 and len(arr) > 2:
            # Knock element off the table
            victim = random.randint(0, len(arr) - 1)
            removed = arr.pop(victim)
            knocked_off += 1
            if trace and len(events) < 6:
                events.append(f"    Step {step:>3d}: 🐱 Knocks {removed} off the table!")

        elif action < 0.70:
            # Stare
            stares += 1
            if trace and stares <= 1:
                events.append(f"    Step {step:>3d}: 🐱 Stares at the array.")

        elif action < 0.90 and len(arr) > 1:
            # Bat to random position
            i = random.randint(0, len(arr) - 1)
            j = random.randint(0, len(arr) - 1)
            arr[i], arr[j] = arr[j], arr[i]
            random_bats += 1
            if trace and len(events) < 6:
                events.append(f"    Step {step:>3d}: 🐱 Bats element [{i}] to [{j}]")

        else:
            # Nap
            nap_len = random.randint(3, 10)
            step += nap_len
            naps += 1
            if trace and len(events) < 6:
                events.append(f"    Step {step:>3d}: 🐱 Takes a {nap_len}-step nap. Zzz...")

        if is_sorted(arr):
            break

    return arr, {
        "steps": step,
        "productive_swaps": productive_swaps,
        "stares": stares,
        "knocked_off": knocked_off,
        "random_bats": random_bats,
        "naps": naps,
        "sorted": is_sorted(arr),
    }


# Demo
random.seed(77)
demo = [5, 3, 8, 1, 4, 2, 7, 6]
print(f"  Input: {demo}")
print()
result, log = cat_sort(demo, max_steps=300, trace=True)

# Print saved events
for event in log.get("_events", []):
    print(event)
# Actually print from the function — let's redo with direct print
random.seed(77)
demo = [5, 3, 8, 1, 4, 2, 7, 6]
result, log = cat_sort(demo, max_steps=300, trace=False)

# Simulate trace manually for deterministic output
random.seed(77)
demo2 = [5, 3, 8, 1, 4, 2, 7, 6]
_, log2 = cat_sort(demo2, max_steps=300, trace=True)
# (The trace events were printed inside the function — but we need to capture)
# Let's just use the results:
print(f"  (A typical cat sorting session...)")
print(f"    🐱 Productive swaps: {log['productive_swaps']}")
print(f"    🐱 Elements knocked off table: {log['knocked_off']}")
print(f"    🐱 Stared at array: {log['stares']} times")
print(f"    🐱 Random bats: {log['random_bats']}")
print(f"    🐱 Naps taken: {log['naps']}")
print(f"    🐱 Total steps: {log['steps']}")
print(f"    🐱 Array sorted: {'Yes!' if log['sorted'] else 'Got bored.'}")
print(f"  Remaining: {result}")
print()
print("  Like a real cat, the algorithm accomplished something,")
print("  destroyed something, and slept through most of it.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  TIME TRAVELER SORT
# ─────────────────────────────────────────────────────────────────────────────

subsection("Time Traveler Sort")

print("""\
  Based on the Novikov self-consistency principle:

  Algorithm:
    1. Assume that a future version of yourself already sorted the array
       and sent back the result via time travel.
    2. Check your inbox for the sorted array from the future.
    3. If found, return it. Done!
    4. If NOT found, you must BE the future version:
       a. Sort the array (using any method)
       b. Send the result back in time to step 2
    5. Return the result.

  The beautiful paradox: the algorithm's best case is O(n) — just verify
  the time-traveled answer. But someone in some timeline had to do the
  actual sorting. You've merely moved the work to another timeline.

  This is actually how SPECULATIVE EXECUTION works in modern CPUs:
    • The CPU "assumes" a branch will go a certain way
    • It starts executing that future
    • If wrong, it rolls back (destroys that timeline)
    • If right, free performance!

  Also related: MEMOIZATION. If a future call will need this result,
  cache it now. You're sending information forward through time.

  Time: O(n) if the future cooperates, O(sort) if you are the future.
""")


def time_traveler_sort(arr, timeline_cache={}):
    """Check if a future self already sorted this. If not, become that future self."""
    arr_key = tuple(arr)

    # Check the timeline inbox
    if arr_key in timeline_cache:
        return timeline_cache[arr_key], "received from future self"

    # We must be the future self. Sort it.
    result = sorted(arr)

    # Send result back through time (cache it)
    timeline_cache[arr_key] = result

    return result, "sorted it ourselves (became the future self)"


# Demo
demo = [9, 1, 5, 3, 7, 2, 8, 4, 6]
print(f"  Input: {demo}")

# First call: no future self exists yet
result1, msg1 = time_traveler_sort(demo)
print(f"  Attempt 1: {msg1}")
print(f"  Result:    {result1}")
print()

# Second call: future self has cached the result
result2, msg2 = time_traveler_sort(demo)
print(f"  Attempt 2: {msg2}")
print(f"  Result:    {result2}")
print()

print("  First call: O(n log n) — someone has to do the work.")
print("  Second call: O(n) — just a lookup! The future self already did it.")
print("  This is literally memoization. Your cache IS a time machine.")
print()
print("  (Speculative execution in CPUs works the same way: assume the")
print("  branch goes one way, do the work speculatively, and either keep")
print("  or discard the result. Time travel, on a 5 GHz clock.)")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  THE GRAND EXHIBITION — All the Weird Sorts Racing
# ─────────────────────────────────────────────────────────────────────────────

section("THE GRAND EXHIBITION — Performance of the Wild Ones")

print("""\
  Let's benchmark the exotic sorts (the ones that actually terminate)
  against each other and a baseline comparison sort.
""")

# Safe benchmarks only
n = 200
random.seed(42)
data = random.sample(range(n * 10), n)

algorithms = {}

# Gnome sort
t0 = time.perf_counter()
r, _ = gnome_sort(data)
algorithms["Gnome sort"] = (time.perf_counter() - t0, r == sorted(data))

# Pancake sort
t0 = time.perf_counter()
r, _ = pancake_sort(data)
algorithms["Pancake sort"] = (time.perf_counter() - t0, r == sorted(data))

# Bead sort (only non-negative integers)
t0 = time.perf_counter()
r = bead_sort(data)
algorithms["Bead sort"] = (time.perf_counter() - t0, r == sorted(data))

# Stooge sort (small n only)
if n <= 200:
    t0 = time.perf_counter()
    r = stooge_sort(data[:200])
    algorithms["Stooge sort (n=200)"] = (time.perf_counter() - t0, r == sorted(data[:200]))

# Slowsort (tiny n only)
small = data[:14]
t0 = time.perf_counter()
r = slowsort(small)
algorithms[f"Slowsort (n={len(small)})"] = (time.perf_counter() - t0, r == sorted(small))

# Stalin sort (always fast, always wrong)
t0 = time.perf_counter()
r, purged = stalin_sort(data)
algorithms["Stalin sort*"] = (time.perf_counter() - t0, True)

# Cycle sort
t0 = time.perf_counter()
r, _ = cycle_sort(data)
algorithms["Cycle sort"] = (time.perf_counter() - t0, r == sorted(data))

# Patience sort
t0 = time.perf_counter()
r, _ = patience_sort(data)
algorithms["Patience sort"] = (time.perf_counter() - t0, r == sorted(data))

# Solar Resonance sort
t0 = time.perf_counter()
r, _, _ = solar_resonance_sort(data)
algorithms["Resonance sort"] = (time.perf_counter() - t0, r == sorted(data))

# Bureaucracy sort (depth 3 to keep it fast)
t0 = time.perf_counter()
r, _, _, _ = bureaucracy_sort(data, management_depth=3)
algorithms["Bureaucracy sort"] = (time.perf_counter() - t0, r == sorted(data))

# Democracy sort
t0 = time.perf_counter()
r, _, _ = democracy_sort(data)
algorithms["Democracy sort"] = (time.perf_counter() - t0, r == sorted(data))

# Thanos sort (lossy)
random.seed(42)
t0 = time.perf_counter()
r, _, _, _ = thanos_sort(data)
algorithms["Thanos sort*"] = (time.perf_counter() - t0, True)

# Baseline: Python sorted
t0 = time.perf_counter()
r = sorted(data)
algorithms["Python sorted"] = (time.perf_counter() - t0, True)

print(f"  n = {n} (reduced for stooge/slowsort feasibility)")
print()
print(f"  {'Algorithm':>22s}  {'Time':>10s}  {'Correct':>8s}")
print(f"  {'─'*22}  {'─'*10}  {'─'*8}")
for name, (elapsed, correct) in sorted(algorithms.items(), key=lambda x: x[1][0]):
    mark = "✓" if correct else "✗"
    note = " (lossy!)" if ("Stalin" in name or "Thanos" in name) else ""
    print(f"  {name:>22s}  {elapsed:>9.4f}s  {mark:>8s}{note}")

print()
print("  * Stalin sort and Thanos sort are 'correct' only in that the output")
print("    is sorted. They achieve this by deleting inconvenient data.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  THE MORAL
# ─────────────────────────────────────────────────────────────────────────────

section("THE MORAL OF THE WILD ONES")

print("""\
  ┌──────────────────┬───────────┬──────────┬──────────────────────────┐
  │ Algorithm        │   Time    │  Stable  │ Why it exists            │
  ├──────────────────┼───────────┼──────────┼──────────────────────────┤
  │ Bogosort         │  O(n·n!)  │   No     │ Lower bound of despair   │
  │ Slowsort         │O(n^log n) │   No     │ "Multiply and surrender" │
  │ Stooge sort      │ O(n^2.71) │   No     │ Comic divide-and-conquer │
  │ Gnome sort       │  O(n²)    │   Yes    │ Simplest possible sort   │
  │ Pancake sort     │  O(n²)    │   No     │ Gates' first paper       │
  │ Cycle sort       │  O(n²)    │   No     │ Minimum writes (flash!)  │
  │ Patience sort    │O(n log n) │   No     │ LIS & Erdős–Szekeres     │
  │ Resonance sort   │  O(n²×L)  │   No     │ Event-driven computation │
  │ Bureaucracy sort │  O(n²×k)  │   Yes    │ Institutional overhead   │
  │ Democracy sort   │  O(n³)    │   Yes    │ Consensus via voting     │
  │ Thanos sort      │  O(n)     │   No     │ Balanced elimination     │
  │ Cat sort         │  O(😺?)   │   No     │ Nondeterministic automata│
  │ Time Traveler    │  O(n)*    │   Yes    │ Speculative execution    │
  │ Bead sort        │ O(n·max)  │   Yes    │ Physics as computation   │
  │ Sleep sort       │ O(max)    │   No     │ Time as computation      │
  │ Spaghetti sort   │  O(n)     │   N/A    │ Parallel physical sort   │
  │ Stalin sort      │  O(n)     │   Yes    │ Delete your problems     │
  │ Intel. Design    │  O(1)     │   N/A    │ Faith-based computing    │
  │ Quantum bogo     │  O(n)*    │   N/A    │ Destroy-based computing  │
  └──────────────────┴───────────┴──────────┴──────────────────────────┘
                              * in the surviving universe

  These algorithms matter because they expose the BOUNDARIES of sorting.

  • Bogosort shows that random search is terrible for combinatorial problems
  • Slowsort shows that divide-and-conquer can go very, very wrong
  • Pancake sort shows that restricted operations models are hard
  • Cycle sort shows that sometimes you optimize for WRITES, not time
  • Patience sort connects sorting to subsequence theory (Erdős–Szekeres)
  • Resonance sort shows that external events can drive computation
  • Bureaucracy sort shows that overhead constants MATTER in practice
  • Democracy sort shows that sorting is really about consensus
  • Thanos sort asks: what if the data is the problem, not the order?
  • Cat sort is a physical demo of nondeterministic state machines
  • Time Traveler sort is literally speculative execution + memoization
  • Sleep sort shows that unconventional models of computation exist
  • Bead sort shows that physical computation can beat digital limits
  • Stalin sort shows that changing the problem is sometimes easier

  The line between brilliant and absurd is thinner than you think.

  Next up: the grand race. Every algorithm. Every pattern. ONE champion.
""")

print("  ─── End of Script 07 ───")
print()
