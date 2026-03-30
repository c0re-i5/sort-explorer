#!/usr/bin/env python3
"""
01_the_naive_sorts.py — Why Does Order Matter?

We start where humanity started: with a pile of things that need to be in order.
Librarians sort books. Mail carriers sort letters. Your brain sorts options by
desirability before you even decide what to eat. Sorting is so fundamental that
we barely notice we're doing it.

But a computer doesn't have intuition. It has comparisons and swaps, and the
question is: how many of each does it take? The answer to that question is
one of the deepest results in computer science, and the journey to it starts
here — with the algorithms that get it wrong, slowly, beautifully, and
instructively.

Topics: why sorting matters · inversions as disorder · bubble sort · the cocktail
shaker · selection sort · insertion sort · the card player's algorithm · quadratic
time and why it's a wall · ASCII visualizations that let you watch order emerge
"""

import random
import time
import math

# ─────────────────────────────────────────────────────────────────────────────
#  WHY SORT?
# ─────────────────────────────────────────────────────────────────────────────

def section(title):
    """Print a section divider."""
    w = 72
    print()
    print("═" * w)
    print(f"  {title}")
    print("═" * w)
    print()


def subsection(title):
    """Print a subsection divider."""
    print()
    print(f"  ── {title} ──")
    print()


section("WHY DOES ORDER MATTER?")

print("""\
  You're looking for a word in a dictionary. The dictionary has 100,000 words.

  If the words are ordered (sorted alphabetically):
    → Binary search: ⌈log₂(100,000)⌉ = 17 lookups. Done.

  If the words are in random order:
    → Linear search: on average 50,000 lookups. Might need all 100,000.

  That's the difference between finding a word in 17 steps and 50,000.
  Not 3× faster. Not 10×. Nearly 3,000× faster.

  Sorting is the invisible infrastructure of nearly everything:
    • Databases sort indexes so queries run in milliseconds, not minutes
    • Search engines sort results by relevance (PageRank)
    • Graphics pipelines sort triangles by depth for correct rendering
    • Operating systems sort processes by priority for scheduling
    • Your contacts app, your file browser, your music library — all sorted

  The question isn't whether to sort. It's how.
""")


# ─────────────────────────────────────────────────────────────────────────────
#  MEASURING DISORDER: INVERSIONS
# ─────────────────────────────────────────────────────────────────────────────

section("MEASURING DISORDER: INVERSIONS")

print("""\
  Before we sort, we need a way to measure how *unsorted* something is.
  The answer: count the inversions.

  An INVERSION is a pair (i, j) where i < j but arr[i] > arr[j].
  In other words: two elements that are in the wrong order relative to each other.

  A sorted array has 0 inversions.
  A reversed array has n(n-1)/2 inversions — the maximum possible.
  A random array has, on average, n(n-1)/4 inversions.

  Every swap of adjacent elements fixes exactly one inversion.
  So any algorithm that only swaps adjacent elements must do at least as many
  swaps as there are inversions. This is why bubble sort is slow on reversed data.
""")


def count_inversions(arr):
    """Count inversions by brute force: O(n²)."""
    n = len(arr)
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            if arr[i] > arr[j]:
                count += 1
    return count


# Demonstrate inversions
examples = {
    "Sorted":         [1, 2, 3, 4, 5],
    "One swap away":  [1, 3, 2, 4, 5],
    "Random":         [3, 1, 5, 2, 4],
    "Reversed":       [5, 4, 3, 2, 1],
}

print("  Array                Inversions    Max possible")
print("  " + "─" * 52)
for label, arr in examples.items():
    n = len(arr)
    inv = count_inversions(arr)
    max_inv = n * (n - 1) // 2
    print(f"  {label:20s} {str(arr):20s} {inv:4d}    / {max_inv}")

print()


# ─────────────────────────────────────────────────────────────────────────────
#  ASCII VISUALIZATION ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def show_array_bars(arr, highlight=None, highlight2=None, label="", width=60):
    """
    Print an ASCII bar chart of the array.
    highlight: index to mark with ██ (active element)
    highlight2: index to mark with ▓▓ (comparison/swap partner)
    """
    if not arr:
        return
    max_val = max(arr)
    bar_max = width - 20  # leave room for labels

    lines = []
    for i, val in enumerate(arr):
        bar_len = int(val / max_val * bar_max) if max_val > 0 else 0
        if highlight is not None and i == highlight:
            bar = "██" * (bar_len // 2 + 1)
            marker = " ◄"
        elif highlight2 is not None and i == highlight2:
            bar = "▓▓" * (bar_len // 2 + 1)
            marker = " ◄"
        else:
            bar = "░░" * (bar_len // 2 + 1)
            marker = ""
        lines.append(f"  {i:2d} │{bar[:bar_len]}{marker}")

    if label:
        print(f"  {label}")
    for line in lines:
        print(line)
    print()


def show_sort_trace(name, arr, steps, max_display=12):
    """Show up to max_display snapshots from a sorting trace."""
    if len(steps) <= max_display:
        selected = steps
    else:
        # Always show first, last, and evenly spaced middle steps
        indices = [0]
        step_size = (len(steps) - 1) / (max_display - 1)
        for i in range(1, max_display - 1):
            indices.append(int(i * step_size))
        indices.append(len(steps) - 1)
        selected = [steps[i] for i in indices]

    print(f"  {name}: {len(steps)} steps total (showing {len(selected)})")
    print()
    for snapshot in selected:
        state, label, h1, h2 = snapshot
        show_array_bars(state, highlight=h1, highlight2=h2, label=label)


# ─────────────────────────────────────────────────────────────────────────────
#  BUBBLE SORT — The One Everyone Knows
# ─────────────────────────────────────────────────────────────────────────────

section("BUBBLE SORT — The One Everyone Knows")

print("""\
  The idea is almost too simple: walk through the array, compare adjacent pairs,
  and swap if they're in the wrong order. Repeat until nothing changes.

  It's called "bubble" sort because larger elements "bubble" up to the end,
  like air bubbles rising through water.

  The tragedy of bubble sort: it's the first sort most people learn,
  and it's the worst practical sort ever devised. It has no situation where
  it's the best choice. Insertion sort beats it on nearly-sorted data.
  Selection sort beats it on swap cost. Even a shuffled deck sorts faster
  with insertion sort in your hands.

  But it's *instructive*. Its failure mode teaches you what not to do,
  and its simplicity makes the analysis crystal clear.
""")

print("  The Algorithm:")
print("  ─────────────")
print("""\
  def bubble_sort(arr):
      n = len(arr)
      for i in range(n):
          swapped = False
          for j in range(n - 1 - i):        # Last i elements already in place
              if arr[j] > arr[j + 1]:
                  arr[j], arr[j + 1] = arr[j + 1], arr[j]
                  swapped = True
          if not swapped:                    # Early exit if already sorted
              break
      return arr
""")


def bubble_sort_traced(arr):
    """Bubble sort with step recording for visualization."""
    arr = arr[:]
    n = len(arr)
    steps = [(arr[:], "Initial state", None, None)]
    comparisons = 0
    swaps = 0

    for i in range(n):
        swapped = False
        for j in range(n - 1 - i):
            comparisons += 1
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1
                swapped = True
                steps.append((arr[:], f"Pass {i+1}: swap [{j}]↔[{j+1}]", j, j + 1))
        if not swapped:
            steps.append((arr[:], f"Pass {i+1}: no swaps — done early!", None, None))
            break
        else:
            steps.append((arr[:], f"Pass {i+1} complete ({n-1-i} elements compared)", None, n - 1 - i))

    return arr, steps, comparisons, swaps


# Demonstrate on a small array
demo = [5, 3, 8, 1, 9, 2, 7, 4, 6]
print(f"  Sorting: {demo}")
print()

result, steps, comps, swps = bubble_sort_traced(demo)
show_sort_trace("Bubble Sort", demo, steps, max_display=8)
print(f"  Result: {result}")
print(f"  Comparisons: {comps}  |  Swaps: {swps}")
print()

subsection("Bubble Sort's Shame: The Reversed Array")

reversed_arr = list(range(8, 0, -1))
_, steps_rev, comps_rev, swps_rev = bubble_sort_traced(reversed_arr)
print(f"  Input:  {reversed_arr}")
print(f"  This is the worst case. Every element must travel the maximum distance.")
print(f"  Comparisons: {comps_rev}  |  Swaps: {swps_rev}")
print(f"  For n={len(reversed_arr)}: n(n-1)/2 = {len(reversed_arr)*(len(reversed_arr)-1)//2}")
print()

subsection("Bubble Sort's Redemption: The Nearly-Sorted Array")

nearly = [1, 2, 3, 5, 4, 6, 7, 8]
_, steps_nearly, comps_nearly, swps_nearly = bubble_sort_traced(nearly)
print(f"  Input:  {nearly}")
print(f"  Only one pair out of order → only one swap needed, then early exit.")
print(f"  Comparisons: {comps_nearly}  |  Swaps: {swps_nearly}")
print(f"  Best case: O(n) — one pass finds nothing to swap and quits.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  COCKTAIL SHAKER SORT — Bubble Sort's Cooler Sibling
# ─────────────────────────────────────────────────────────────────────────────

section("COCKTAIL SHAKER SORT — Bubble Sort's Cooler Sibling")

print("""\
  Bubble sort only moves elements in one direction per pass. A small element
  at the end takes n passes to reach the front — the "turtle problem."

  Cocktail shaker sort (bidirectional bubble sort) alternates direction:
  left-to-right, then right-to-left, like shaking a cocktail. Turtles move
  faster because they get pushed in both directions.

  It's still O(n²), but with a smaller constant. And it has a great name.
""")


def cocktail_shaker_traced(arr):
    """Cocktail shaker sort with tracing."""
    arr = arr[:]
    n = len(arr)
    steps = [(arr[:], "Initial state", None, None)]
    comparisons = 0
    swaps = 0
    start = 0
    end = n - 1

    while start < end:
        new_end = start
        for j in range(start, end):
            comparisons += 1
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1
                new_end = j
        end = new_end
        steps.append((arr[:], f"→ Forward pass done", None, None))

        new_start = end
        for j in range(end, start, -1):
            comparisons += 1
            if arr[j - 1] > arr[j]:
                arr[j - 1], arr[j] = arr[j], arr[j - 1]
                swaps += 1
                new_start = j
        start = new_start
        steps.append((arr[:], f"← Backward pass done", None, None))

    return arr, steps, comparisons, swaps


# The turtle problem demonstration
turtle_arr = [2, 3, 4, 5, 6, 7, 8, 1]  # 1 is a "turtle" at the end
print(f"  The turtle problem: {turtle_arr}")
print(f"  Element 1 is trapped at the end — a 'turtle.'")
print()

_, _, b_comps, b_swaps = bubble_sort_traced(turtle_arr)
_, _, c_comps, c_swaps = cocktail_shaker_traced(turtle_arr)

print(f"  Bubble sort:          {b_comps:3d} comparisons, {b_swaps:3d} swaps")
print(f"  Cocktail shaker sort: {c_comps:3d} comparisons, {c_swaps:3d} swaps")
print(f"  Cocktail shaker wins by moving the turtle leftward on backward passes.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  SELECTION SORT — Minimizing Swaps
# ─────────────────────────────────────────────────────────────────────────────

section("SELECTION SORT — Minimizing Swaps")

print("""\
  Selection sort takes a different approach: find the minimum, put it first.
  Find the next minimum, put it second. Repeat.

  The appeal: it does exactly n-1 swaps, regardless of input. If swaps are
  expensive (writing to flash memory, moving physical objects), selection sort
  is optimal.

  The drawback: it always does n(n-1)/2 comparisons. It can't exit early.
  It doesn't care if the data is nearly sorted — it'll do the same work.
  That stubbornness makes it worse than insertion sort in almost every
  practical scenario.

  But it's beautifully simple, and every iteration puts one element into
  its final position. You can watch the sorted region grow from the left.
""")

print("  The Algorithm:")
print("  ─────────────")
print("""\
  def selection_sort(arr):
      n = len(arr)
      for i in range(n):
          min_idx = i
          for j in range(i + 1, n):
              if arr[j] < arr[min_idx]:
                  min_idx = j
          arr[i], arr[min_idx] = arr[min_idx], arr[i]
      return arr
""")


def selection_sort_traced(arr):
    """Selection sort with step recording."""
    arr = arr[:]
    n = len(arr)
    steps = [(arr[:], "Initial state", None, None)]
    comparisons = 0
    swaps = 0

    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            comparisons += 1
            if arr[j] < arr[min_idx]:
                min_idx = j
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            swaps += 1
            steps.append((arr[:], f"Round {i+1}: min={arr[i]}, swapped [{i}]↔[{min_idx}]", i, min_idx))
        else:
            steps.append((arr[:], f"Round {i+1}: {arr[i]} already in place", i, None))

    return arr, steps, comparisons, swaps


demo = [5, 3, 8, 1, 9, 2, 7, 4, 6]
print(f"  Sorting: {demo}")
print()

result, steps, comps, swps = selection_sort_traced(demo)
show_sort_trace("Selection Sort", demo, steps, max_display=10)
print(f"  Result: {result}")
print(f"  Comparisons: {comps}  |  Swaps: {swps}")
print(f"  Note: exactly {len(demo) - 1} swaps (or fewer if elements were in place).")
print()

subsection("Selection Sort's Indifference")

print("  Selection sort doesn't care about the input order:")
for label, data in [("Random", [5, 3, 8, 1, 9, 2, 7, 4, 6]),
                     ("Sorted", [1, 2, 3, 4, 5, 6, 7, 8, 9]),
                     ("Reversed", [9, 8, 7, 6, 5, 4, 3, 2, 1])]:
    _, _, c, s = selection_sort_traced(data)
    print(f"  {label:10s} → Comparisons: {c:3d}  |  Swaps: {s}")
print()
print("  Same comparisons every time. Selection sort is stubbornly O(n²).")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  INSERTION SORT — The Card Player's Algorithm
# ─────────────────────────────────────────────────────────────────────────────

section("INSERTION SORT — The Card Player's Algorithm")

print("""\
  Pick up cards one at a time. Each new card, slide it into the right place
  among the cards already in your hand. That's insertion sort.

  This is how most humans sort when they have a small collection:
    • Sorting a hand of playing cards
    • Alphabetizing papers on a desk
    • Putting books back on a shelf

  And it has a secret superpower: it's adaptive.

  On nearly-sorted data, insertion sort approaches O(n). Its running time
  is O(n + d), where d is the number of inversions. If d is small, insertion
  sort is fast — sometimes faster than O(n log n) algorithms on small inputs.

  This is why:
    • Python's Timsort uses insertion sort for small runs
    • C++ std::sort switches to insertion sort below ~16 elements
    • Java's dual-pivot quicksort falls back to insertion sort too
""")

print("  The Algorithm:")
print("  ─────────────")
print("""\
  def insertion_sort(arr):
      for i in range(1, len(arr)):
          key = arr[i]
          j = i - 1
          while j >= 0 and arr[j] > key:
              arr[j + 1] = arr[j]          # Slide right
              j -= 1
          arr[j + 1] = key                 # Insert
      return arr
""")


def insertion_sort_traced(arr):
    """Insertion sort with step recording."""
    arr = arr[:]
    n = len(arr)
    steps = [(arr[:], "Initial state", None, None)]
    comparisons = 0
    swaps = 0  # counting shifts as swaps for consistency

    for i in range(1, n):
        key = arr[i]
        j = i - 1
        shifts = 0
        while j >= 0 and arr[j] > key:
            comparisons += 1
            arr[j + 1] = arr[j]
            shifts += 1
            swaps += 1
            j -= 1
        if j >= 0:
            comparisons += 1  # The failing comparison
        arr[j + 1] = key
        label = f"Insert {key}: shifted {shifts} element{'s' if shifts != 1 else ''}"
        steps.append((arr[:], label, j + 1, i if shifts > 0 else None))

    return arr, steps, comparisons, swaps


demo = [5, 3, 8, 1, 9, 2, 7, 4, 6]
print(f"  Sorting: {demo}")
print()

result, steps, comps, swps = insertion_sort_traced(demo)
show_sort_trace("Insertion Sort", demo, steps, max_display=10)
print(f"  Result: {result}")
print(f"  Comparisons: {comps}  |  Shifts: {swps}")
print()

subsection("Insertion Sort's Superpower: Nearly Sorted Data")

print("  Insertion sort adapts to existing order:")
patterns = [
    ("Random",        [5, 3, 8, 1, 9, 2, 7, 4, 6]),
    ("Nearly sorted", [1, 2, 4, 3, 5, 6, 8, 7, 9]),
    ("Sorted",        [1, 2, 3, 4, 5, 6, 7, 8, 9]),
    ("Reversed",      [9, 8, 7, 6, 5, 4, 3, 2, 1]),
]

for label, data in patterns:
    inv = count_inversions(data)
    _, _, c, s = insertion_sort_traced(data)
    print(f"  {label:16s} → Inversions: {inv:3d}  |  Comparisons: {c:3d}  |  Shifts: {s:3d}")

print()
print("  Notice: comparisons ≈ inversions + n. The more sorted the data,")
print("  the faster insertion sort runs. On sorted data: O(n). On reversed: O(n²).")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  BINARY INSERTION SORT — Reducing Comparisons
# ─────────────────────────────────────────────────────────────────────────────

section("BINARY INSERTION SORT — When You Can Search Faster")

print("""\
  Insertion sort spends time finding where to insert (linear scan backwards).
  But the already-sorted portion is... sorted. We can binary search it!

  Binary insertion sort uses O(n log n) comparisons — optimal. But it still
  does O(n²) shifts, because you can't insert into the middle of a contiguous
  array without moving everything over.

  It's like knowing exactly where a book goes on the shelf (fast lookup),
  but still having to slide every book over to make room (slow shifting).

  The lesson: comparisons aren't everything. Data movement matters too.
""")


def binary_insertion_sort_traced(arr):
    """Binary insertion sort with step recording."""
    arr = arr[:]
    n = len(arr)
    steps = [(arr[:], "Initial state", None, None)]
    comparisons = 0
    shifts = 0

    for i in range(1, n):
        key = arr[i]
        # Binary search for insertion point
        lo, hi = 0, i
        while lo < hi:
            comparisons += 1
            mid = (lo + hi) // 2
            if arr[mid] <= key:
                lo = mid + 1
            else:
                hi = mid

        # Shift elements right
        for j in range(i, lo, -1):
            arr[j] = arr[j - 1]
            shifts += 1
        arr[lo] = key

        steps.append((arr[:], f"Insert {key} at position {lo} ({i - lo} shifts)", lo, i))

    return arr, steps, comparisons, shifts


demo = [5, 3, 8, 1, 9, 2, 7, 4, 6]
result, steps, comps, shifts = binary_insertion_sort_traced(demo)
print(f"  Sorting: {demo}")
print()
print(f"  Comparisons: {comps} (vs {insertion_sort_traced(demo)[2]} for standard insertion sort)")
print(f"  Shifts: {shifts} (same — we can't avoid moving data)")
print(f"  Result: {result}")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  THE QUADRATIC WALL
# ─────────────────────────────────────────────────────────────────────────────

section("THE QUADRATIC WALL")

print("""\
  Let's see what O(n²) actually means. We'll run all three sorts on
  increasing sizes and time them.

  Spoiler: when n doubles, time quadruples. That's the trap.
""")


def bubble_sort(arr):
    arr = arr[:]
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
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


sizes = [100, 200, 500, 1000, 2000, 5000]

print(f"  {'n':>6s}  {'Bubble':>10s}  {'Selection':>10s}  {'Insertion':>10s}")
print(f"  {'─'*6}  {'─'*10}  {'─'*10}  {'─'*10}")

for n in sizes:
    data = random.sample(range(n * 10), n)

    t0 = time.perf_counter()
    bubble_sort(data)
    t_bubble = time.perf_counter() - t0

    t0 = time.perf_counter()
    selection_sort(data)
    t_select = time.perf_counter() - t0

    t0 = time.perf_counter()
    insertion_sort(data)
    t_insert = time.perf_counter() - t0

    print(f"  {n:>6d}  {t_bubble:>9.4f}s  {t_select:>9.4f}s  {t_insert:>9.4f}s")

print()
print("  Watch the times roughly quadruple when n doubles. That's O(n²).")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  THE CROSSOVER: SORTED VS RANDOM
# ─────────────────────────────────────────────────────────────────────────────

subsection("The Crossover: When Input Pattern Changes Everything")

n = 1000
data_random = random.sample(range(n * 10), n)
data_sorted = list(range(n))
data_reversed = list(range(n, 0, -1))
data_nearly = list(range(n))
# Introduce a few random swaps to "nearly sorted"
for _ in range(n // 50):
    i, j = random.randint(0, n - 1), random.randint(0, n - 1)
    data_nearly[i], data_nearly[j] = data_nearly[j], data_nearly[i]

print(f"  n = {n}")
print()
print(f"  {'Pattern':>16s}  {'Bubble':>10s}  {'Selection':>10s}  {'Insertion':>10s}")
print(f"  {'─'*16}  {'─'*10}  {'─'*10}  {'─'*10}")

for label, data in [("Random", data_random),
                     ("Nearly sorted", data_nearly),
                     ("Sorted", data_sorted),
                     ("Reversed", data_reversed)]:
    t0 = time.perf_counter()
    bubble_sort(data)
    t_b = time.perf_counter() - t0

    t0 = time.perf_counter()
    selection_sort(data)
    t_s = time.perf_counter() - t0

    t0 = time.perf_counter()
    insertion_sort(data)
    t_i = time.perf_counter() - t0

    print(f"  {label:>16s}  {t_b:>9.4f}s  {t_s:>9.4f}s  {t_i:>9.4f}s")

print()
print("  Key observations:")
print("  • Insertion sort on sorted data: blazing fast (O(n))")
print("  • Selection sort: same time regardless — it doesn't care about order")
print("  • Bubble sort on reversed data: worst case — every pair needs swapping")
print("  • Insertion sort adapts. The others (mostly) don't.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  STABILITY: DOES THE ORDER OF EQUALS MATTER?
# ─────────────────────────────────────────────────────────────────────────────

section("STABILITY: DOES THE ORDER OF EQUALS MATTER?")

print("""\
  A sort is STABLE if equal elements keep their original relative order.
  This matters when you sort by multiple keys:

    Sort students by name, then by grade.
    If the grade sort is stable, students with the same grade
    stay in alphabetical order. If not, you lose the name sort.

  Stable:    Bubble sort, Insertion sort, (standard) Merge sort
  Unstable:  Selection sort, Heapsort, (standard) Quicksort

  Let's demonstrate:
""")

students = [
    ("Alice", 85), ("Bob", 92), ("Carol", 85),
    ("Dave", 78), ("Eve", 92), ("Frank", 85),
]

print(f"  Original order (by name):")
for name, grade in students:
    print(f"    {name:8s} {grade}")

# Stable sort (insertion sort by grade)
stable = students[:]
for i in range(1, len(stable)):
    key = stable[i]
    j = i - 1
    while j >= 0 and stable[j][1] > key[1]:
        stable[j + 1] = stable[j]
        j -= 1
    stable[j + 1] = key

print(f"\n  Stable sort by grade (insertion sort):")
for name, grade in stable:
    print(f"    {name:8s} {grade}", end="")
    same_grade = [s[0] for s in students if s[1] == grade]
    if len(same_grade) > 1:
        print(f"  ← same grade group: {', '.join(same_grade)} (order preserved)")
    else:
        print()

# Unstable sort (selection sort by grade)
unstable = students[:]
for i in range(len(unstable)):
    min_idx = i
    for j in range(i + 1, len(unstable)):
        if unstable[j][1] < unstable[min_idx][1]:
            min_idx = j
    unstable[i], unstable[min_idx] = unstable[min_idx], unstable[i]

print(f"\n  Unstable sort by grade (selection sort):")
for name, grade in unstable:
    print(f"    {name:8s} {grade}")

print()
print("  With stable sort, Alice and Carol and Frank (all 85) stay in that order.")
print("  With unstable sort, they might not. Stability is a guarantee, not a hope.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  WATCHING DISORDER DISSOLVE
# ─────────────────────────────────────────────────────────────────────────────

section("WATCHING DISORDER DISSOLVE")

print("""\
  Let's watch inversions decrease as each algorithm runs. This is the heart
  of sorting: disorder → order, measured in real numbers.
""")

random.seed(42)
watch_data = random.sample(range(1, 16), 15)

for name, sort_func in [("Bubble Sort", bubble_sort_traced),
                         ("Selection Sort", selection_sort_traced),
                         ("Insertion Sort", insertion_sort_traced)]:
    _, steps, _, _ = sort_func(watch_data)

    print(f"  {name}:")
    print(f"  {'Step':>6s}  {'Inversions':>10s}  {'Progress bar':30s}")
    print(f"  {'─'*6}  {'─'*10}  {'─'*30}")

    max_inv = count_inversions(watch_data)
    # Sample steps evenly
    n_show = min(10, len(steps))
    indices = [int(i * (len(steps) - 1) / (n_show - 1)) for i in range(n_show)] if n_show > 1 else [0]

    for idx in indices:
        state = steps[idx][0]
        inv = count_inversions(state)
        pct = 1.0 - (inv / max_inv) if max_inv > 0 else 1.0
        bar_len = int(pct * 25)
        bar = "█" * bar_len + "░" * (25 - bar_len)
        print(f"  {idx:>6d}  {inv:>10d}  [{bar}] {pct*100:5.1f}%")

    print()


# ─────────────────────────────────────────────────────────────────────────────
#  COMPARISON SUMMARY TABLE
# ─────────────────────────────────────────────────────────────────────────────

section("THE NAIVE SORTS: A COMPARISON")

print("""\
  ┌─────────────────┬──────────┬──────────┬──────────┬────────┬────────┐
  │ Algorithm       │  Best    │ Average  │  Worst   │ Memory │ Stable │
  ├─────────────────┼──────────┼──────────┼──────────┼────────┼────────┤
  │ Bubble Sort     │  O(n)    │  O(n²)   │  O(n²)   │  O(1)  │  Yes   │
  │ Cocktail Shaker │  O(n)    │  O(n²)   │  O(n²)   │  O(1)  │  Yes   │
  │ Selection Sort  │  O(n²)   │  O(n²)   │  O(n²)   │  O(1)  │  No*   │
  │ Insertion Sort  │  O(n)    │  O(n²)   │  O(n²)   │  O(1)  │  Yes   │
  │ Binary Ins.Sort │  O(n lg n)│ O(n²)   │  O(n²)   │  O(1)  │  Yes   │
  └─────────────────┴──────────┴──────────┴──────────┴────────┴────────┘

  * Selection sort can be made stable, but the standard version isn't.

  Key takeaways:
  • All are O(n²) average/worst — they hit the quadratic wall.
  • Insertion sort is the practical winner: adaptive, stable, fast on small/sorted data.
  • Selection sort minimizes swaps but wastes comparisons.
  • Bubble sort is... educational. That's the nicest thing we can say.

  Next up: breaking the quadratic barrier with divide and conquer.
  Can we do better than O(n²)? The answer is yes — dramatically.
""")

print("  ─── End of Script 01 ───")
print()
