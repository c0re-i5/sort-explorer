#!/usr/bin/env python3
"""
03_heaps_and_trees.py — Structure as Strategy

What if the data structure itself could sort? A heap is an array that
secretly encodes a tree, and that tree enforces a partial order that makes
extracting the minimum (or maximum) take O(log n) time. Build the heap,
then repeatedly extract the max — and you've sorted.

Heapsort is the algorithm that answers the question: "Can we get O(n log n)
worst-case WITHOUT O(n) extra memory?" Yes. Heapsort uses O(1) extra space
and runs in O(n log n) guaranteed. No bad pivots, no extra buffer.

The tradeoff: it's not stable, its constant factor is worse than quicksort
(poor cache behavior), and it has no adaptive mode. But when guarantees and
memory matter, heapsort delivers.

Topics: binary heaps · the heap property · implicit tree in an array · sift-up
and sift-down · BUILD-HEAP in O(n) · heapsort · priority queues · the
connection to Dijkstra's algorithm [← repo 3] · tournament sort · tree sort · BSTs
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
#  THE IMPLICIT BINARY TREE
# ─────────────────────────────────────────────────────────────────────────────

section("THE IMPLICIT BINARY TREE — A Tree Hidden in an Array")

print("""\
  Take an array: [90, 70, 80, 30, 50, 60, 20, 10, 40]

  Pretend it's a tree. Element at index i has:
    • Left child at index  2i + 1
    • Right child at index 2i + 2
    • Parent at index      (i - 1) // 2

  No pointers. No node objects. Just index arithmetic.

  Index:   0   1   2   3   4   5   6   7   8
  Value:  90  70  80  30  50  60  20  10  40
""")


def draw_heap_tree(arr, width=64):
    """Draw a binary heap as an ASCII tree."""
    if not arr:
        return
    n = len(arr)
    depth = math.floor(math.log2(n)) + 1 if n > 0 else 0

    lines = []
    for d in range(depth):
        start = 2**d - 1
        end = min(2**(d+1) - 1, n)
        if start >= n:
            break

        level_vals = [str(arr[i]) if i < n else "" for i in range(start, end)]
        num_in_level = len(level_vals)

        # Spacing: wider at top, narrower at bottom
        total_slots = 2**depth
        spacing = total_slots // (2**d)
        pad = spacing // 2

        line = ""
        for i, val in enumerate(level_vals):
            left_pad = pad if i == 0 else spacing - len(val) // 2
            line += " " * max(0, left_pad - len(val)//2) + val
            if i < len(level_vals) - 1:
                line += " " * max(1, spacing - len(val))

        lines.append("  " + line)

    for line in lines:
        print(line)
    print()


demo_heap = [90, 70, 80, 30, 50, 60, 20, 10, 40]
print("  As a tree:")
print()
draw_heap_tree(demo_heap)

print("""\
  This is a MAX-HEAP: every parent ≥ both children.
    • 90 ≥ 70, 80    ✓
    • 70 ≥ 30, 50    ✓
    • 80 ≥ 60, 20    ✓
    • 30 ≥ 10, 40    ✗  ← Wait, 30 < 40? That's not a valid heap!

  Let's fix that. But first, let's understand the operations.
""")


# ─────────────────────────────────────────────────────────────────────────────
#  HEAP OPERATIONS: SIFT-UP AND SIFT-DOWN
# ─────────────────────────────────────────────────────────────────────────────

section("HEAP OPERATIONS: SIFT-UP AND SIFT-DOWN")

print("""\
  Two fundamental operations maintain the heap property:

  SIFT-UP (a.k.a. bubble up, swim):
    Used after INSERTING at the bottom.
    Compare with parent; if larger, swap up. Repeat until heap property holds.
    O(log n) — you climb at most the height of the tree.

  SIFT-DOWN (a.k.a. bubble down, sink):
    Used after REPLACING the root (e.g., extracting the max).
    Compare with children; swap with the larger child. Repeat downward.
    O(log n) — you descend at most the height of the tree.
""")


def sift_down(arr, n, i, trace=None):
    """Sift element at index i down to restore max-heap property."""
    largest = i
    left = 2 * i + 1
    right = 2 * i + 2

    if left < n and arr[left] > arr[largest]:
        largest = left
    if right < n and arr[right] > arr[largest]:
        largest = right

    if largest != i:
        if trace is not None:
            trace.append(f"    Swap arr[{i}]={arr[i]} ↔ arr[{largest}]={arr[largest]}")
        arr[i], arr[largest] = arr[largest], arr[i]
        sift_down(arr, n, largest, trace)


def sift_up(arr, i, trace=None):
    """Sift element at index i up to restore max-heap property."""
    while i > 0:
        parent = (i - 1) // 2
        if arr[i] > arr[parent]:
            if trace is not None:
                trace.append(f"    Swap arr[{i}]={arr[i]} ↔ arr[{parent}]={arr[parent]}")
            arr[i], arr[parent] = arr[parent], arr[i]
            i = parent
        else:
            break


# Demonstrate sift-down
demo = [30, 70, 80, 90, 50, 60, 20, 10, 40]
print(f"  Array: {demo}")
print(f"  Element at index 0 (value {demo[0]}) violates heap property.")
print(f"  Sift it down:")
trace = []
sift_down(demo, len(demo), 0, trace)
for step in trace:
    print(step)
print(f"  Result: {demo}")
print()
draw_heap_tree(demo)


# ─────────────────────────────────────────────────────────────────────────────
#  BUILD-HEAP: THE O(n) SURPRISE
# ─────────────────────────────────────────────────────────────────────────────

section("BUILD-HEAP — Faster Than You'd Think")

print("""\
  Naive approach: insert n elements one at a time, each sifting up → O(n log n).

  Floyd's approach (1964): start from the last internal node and sift down.
  Leaves are already valid heaps (size 1). Work backward.

  This is O(n) — yes, LINEAR! Not O(n log n).

  Why? Most nodes are near the bottom and sift down only 1–2 levels.
  Only the root sifts down log(n) levels. The sum telescopes:

    Σ (height of node) = n - ⌈log₂(n+1)⌉ ≈ n

  It's counterintuitive but true: building a heap is cheaper than sorting.
""")


def build_max_heap(arr, verbose=False):
    """Build a max-heap in O(n) using Floyd's method."""
    arr = arr[:]
    n = len(arr)
    trace = []

    # Start from last internal node
    for i in range(n // 2 - 1, -1, -1):
        if verbose:
            trace.append(f"  Sift down index {i} (value {arr[i]}):")
        sift_down(arr, n, i, trace if verbose else None)

    return arr, trace


demo = [4, 10, 3, 5, 1, 8, 7, 2, 9, 6]
print(f"  Input: {demo}")
print()

heap, trace = build_max_heap(demo, verbose=True)

for step in trace:
    print(step)

print()
print(f"  Max-heap: {heap}")
print()
draw_heap_tree(heap)

# Verify heap property
def is_max_heap(arr):
    n = len(arr)
    for i in range(n):
        left = 2 * i + 1
        right = 2 * i + 2
        if left < n and arr[i] < arr[left]:
            return False
        if right < n and arr[i] < arr[right]:
            return False
    return True

print(f"  Valid max-heap? {is_max_heap(heap)} ✓")
print()

subsection("BUILD-HEAP Is Truly O(n)")

print("  Timing BUILD-HEAP vs. n×SIFT-UP insertion:")
print()

random.seed(42)
print(f"  {'n':>8s}  {'Floyd (sift-down)':>18s}  {'Naive (sift-up)':>18s}  {'Ratio':>8s}")
print(f"  {'─'*8}  {'─'*18}  {'─'*18}  {'─'*8}")

for n in [10000, 50000, 100000, 500000, 1000000]:
    data = random.sample(range(n * 10), n)

    # Floyd's BUILD-HEAP
    arr1 = data[:]
    t0 = time.perf_counter()
    for i in range(len(arr1) // 2 - 1, -1, -1):
        sift_down(arr1, len(arr1), i)
    t_floyd = time.perf_counter() - t0

    # Naive insertion
    arr2 = []
    t0 = time.perf_counter()
    for val in data:
        arr2.append(val)
        sift_up(arr2, len(arr2) - 1)
    t_naive = time.perf_counter() - t0

    print(f"  {n:>8d}  {t_floyd:>17.4f}s  {t_naive:>17.4f}s  {t_naive/t_floyd:>7.2f}×")

print()
print("  Floyd's method is consistently faster — the theoretical O(n) vs O(n log n)")
print("  shows up clearly in practice.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  HEAPSORT — Extract, Extract, Extract
# ─────────────────────────────────────────────────────────────────────────────

section("HEAPSORT — Sorting by Repeated Extraction")

print("""\
  The algorithm:
    1. Build a max-heap from the array                    — O(n)
    2. For i = n-1 down to 1:                             — n iterations
       a. Swap arr[0] (maximum) with arr[i]               — O(1)
       b. Sift down arr[0] in the heap of size i          — O(log n)
    3. The array is now sorted in ascending order.

  Total: O(n) + n × O(log n) = O(n log n). Worst-case guaranteed.
  Memory: O(1) extra — it sorts in place inside the original array.

  The trick: the "sorted" region grows from the right. The "heap" region
  shrinks from the right. The max keeps getting pulled out and placed at
  the end.
""")


def heapsort_traced(arr):
    """Heapsort with step tracing."""
    arr = arr[:]
    n = len(arr)
    comparisons = [0]
    swaps = [0]

    def sift_down_counted(a, size, i):
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        comparisons[0] += 1 if left < size else 0
        if left < size and a[left] > a[largest]:
            largest = left
        comparisons[0] += 1 if right < size else 0
        if right < size and a[right] > a[largest]:
            largest = right
        if largest != i:
            a[i], a[largest] = a[largest], a[i]
            swaps[0] += 1
            sift_down_counted(a, size, largest)

    # Build max-heap
    for i in range(n // 2 - 1, -1, -1):
        sift_down_counted(arr, n, i)

    build_comps = comparisons[0]
    build_swaps = swaps[0]

    # Extract elements
    steps = [(arr[:], "Max-heap built", 0)]
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        swaps[0] += 1
        sift_down_counted(arr, i, 0)
        steps.append((arr[:], f"Extract max={arr[i]}, heap size={i}", i))

    return arr, steps, comparisons[0], swaps[0], build_comps


demo = [4, 10, 3, 5, 1, 8, 7, 2, 9, 6]
print(f"  Sorting: {demo}")
print()

result, steps, comps, swps, build_comps = heapsort_traced(demo)

# Show a few snapshots
print("  Step-by-step extraction:")
for i, (state, label, boundary) in enumerate(steps):
    if i < 5 or i == len(steps) - 1:
        heap_part = state[:boundary] if boundary > 0 else state
        sorted_part = state[boundary:] if boundary > 0 else []
        print(f"    {label:40s}  heap={heap_part}  sorted={sorted_part}")
    elif i == 5:
        print(f"    {'...':40s}")

print()
print(f"  Result: {result}")
print(f"  Comparisons: {comps} ({build_comps} for BUILD-HEAP + {comps - build_comps} for extractions)")
print(f"  Swaps: {swps}")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  PRIORITY QUEUES — The Real-World Application
# ─────────────────────────────────────────────────────────────────────────────

section("PRIORITY QUEUES — Why Heaps Really Matter")

print("""\
  Heapsort is interesting, but the real star is the PRIORITY QUEUE — a data
  structure built on a heap that supports:
    • INSERT(element, priority):  O(log n)
    • EXTRACT-MIN/MAX():          O(log n)
    • PEEK():                     O(1)

  Priority queues are everywhere:
    • Dijkstra's algorithm uses a min-heap to always expand the cheapest
      node [← repo 3: navigational pathfinding]
    • A* uses a min-heap keyed on f(n) = g(n) + h(n) [← repo 3]
    • CPU schedulers pick the highest-priority process
    • Event simulation processes the next event in time order
    • Huffman coding builds the tree bottom-up using a min-heap [← repo 1]

  Let's build one and simulate a hospital emergency room:
""")


class MinHeap:
    """Simple min-heap priority queue."""

    def __init__(self):
        self.data = []

    def push(self, priority, item):
        self.data.append((priority, item))
        self._sift_up(len(self.data) - 1)

    def pop(self):
        if not self.data:
            return None
        self.data[0], self.data[-1] = self.data[-1], self.data[0]
        result = self.data.pop()
        if self.data:
            self._sift_down(0)
        return result

    def peek(self):
        return self.data[0] if self.data else None

    def __len__(self):
        return len(self.data)

    def _sift_up(self, i):
        while i > 0:
            parent = (i - 1) // 2
            if self.data[i][0] < self.data[parent][0]:
                self.data[i], self.data[parent] = self.data[parent], self.data[i]
                i = parent
            else:
                break

    def _sift_down(self, i):
        n = len(self.data)
        while True:
            smallest = i
            left = 2 * i + 1
            right = 2 * i + 2
            if left < n and self.data[left][0] < self.data[smallest][0]:
                smallest = left
            if right < n and self.data[right][0] < self.data[smallest][0]:
                smallest = right
            if smallest != i:
                self.data[i], self.data[smallest] = self.data[smallest], self.data[i]
                i = smallest
            else:
                break


# Hospital ER simulation
print("  🏥 Emergency Room Triage Simulation")
print("  Priority 1 = most urgent (treated first)")
print()

er = MinHeap()
patients = [
    (3, "Alice — broken arm"),
    (1, "Bob — cardiac arrest"),
    (5, "Carol — mild headache"),
    (2, "Dave — severe bleeding"),
    (4, "Eve — sprained ankle"),
    (1, "Frank — stroke symptoms"),
    (3, "Grace — deep laceration"),
]

print("  Arrivals:")
for priority, patient in patients:
    er.push(priority, patient)
    print(f"    Priority {priority}: {patient}")

print()
print("  Treatment order (min-heap extracts lowest priority number first):")
order = 1
while len(er) > 0:
    priority, patient = er.pop()
    print(f"    {order}. [Priority {priority}] {patient}")
    order += 1

print()
print("  Bob and Frank (both priority 1) go first. Carol (priority 5) waits.")
print("  The heap ensures we always treat the most urgent patient next,")
print("  with O(log n) insertion and extraction — not O(n) scanning.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  THE DIJKSTRA CONNECTION
# ─────────────────────────────────────────────────────────────────────────────

subsection("The Dijkstra Connection [← Repo 3]")

print("""\
  In repo 3 (Navigational Pathfinding), Dijkstra's algorithm finds the
  shortest path by always expanding the cheapest unexplored node. That
  "always expand the cheapest" is exactly EXTRACT-MIN from a priority queue.

  Without a heap: Dijkstra is O(V²) — scan all vertices to find the minimum.
  With a binary heap: Dijkstra is O((V + E) log V) — extract-min in O(log V).
  With a Fibonacci heap: Dijkstra is O(V log V + E) — even better, but complex.

  The heap is what makes Dijkstra fast. And now you know how it works.

  Similarly, A* uses a min-heap keyed on f(n) = g(n) + h(n), and the
  Wave Interference Pathfinder from repo 3 uses a heap to process
  wavefronts in arrival-time order — just like the Fast Marching Method
  from repo 4 (Waveguides).
""")


# ─────────────────────────────────────────────────────────────────────────────
#  TOURNAMENT SORT — Sorting by Competition
# ─────────────────────────────────────────────────────────────────────────────

section("TOURNAMENT SORT — Sorting by Competition")

print("""\
  Imagine a single-elimination tournament bracket. Each match compares two
  elements; the winner (smaller) advances. After all matches, the overall
  winner is the minimum.

  Remove the winner, replay only its matches, and the second-place
  emerges. Repeat for all n elements.

  Finding the first minimum: n - 1 comparisons (same as any tournament).
  Finding each subsequent minimum: log₂(n) comparisons (replaying one branch).
  Total: n - 1 + (n-1)·log₂(n) ≈ O(n log n).

  Tournament sort is historically important — it's how replacement selection
  works in external sorting (Script 06), and it's how you find the
  second-smallest element with the minimum number of comparisons.
""")


def tournament_sort(arr):
    """Tournament sort: build a tournament tree, extract winners."""
    n = len(arr)
    INF = float('inf')

    # Build complete binary tree with leaves = array elements
    # Tree size: next power of 2 ≥ n, doubled for internal nodes
    size = 1
    while size < n:
        size *= 2

    tree = [INF] * (2 * size)
    source = [(-1, -1)] * (2 * size)  # Track which leaf produced each value

    # Place elements in leaves
    for i in range(n):
        tree[size + i] = arr[i]
        source[size + i] = (i, arr[i])

    # Build tournament (internal nodes = min of children)
    for i in range(size - 1, 0, -1):
        if tree[2 * i] <= tree[2 * i + 1]:
            tree[i] = tree[2 * i]
            source[i] = source[2 * i]
        else:
            tree[i] = tree[2 * i + 1]
            source[i] = source[2 * i + 1]

    result = []
    comparisons = 0

    for _ in range(n):
        # Winner is at root
        result.append(tree[1])
        winner_leaf = source[1][0]

        # Remove winner by setting its leaf to infinity
        pos = size + winner_leaf
        tree[pos] = INF
        source[pos] = (-1, INF)

        # Replay matches up the tree
        pos //= 2
        while pos >= 1:
            comparisons += 1
            left, right = 2 * pos, 2 * pos + 1
            if tree[left] <= tree[right]:
                tree[pos] = tree[left]
                source[pos] = source[left]
            else:
                tree[pos] = tree[right]
                source[pos] = source[right]
            pos //= 2

    return result, comparisons


demo = [7, 3, 9, 1, 5, 8, 2, 6]
print(f"  Input: {demo}")
result, comps = tournament_sort(demo)
print(f"  Sorted: {result}")
print(f"  Comparisons: {comps}")
print(f"  Theory: n - 1 + (n-1)·⌈lg n⌉ ≈ {len(demo)-1 + (len(demo)-1)*math.ceil(math.log2(len(demo)))}")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  TREE SORT — Sorting via Binary Search Trees
# ─────────────────────────────────────────────────────────────────────────────

section("TREE SORT — Sorting via Binary Search Trees")

print("""\
  Simple idea: insert all elements into a Binary Search Tree (BST),
  then do an in-order traversal. The traversal gives you sorted order.

  Average case: O(n log n) — if the tree stays balanced.
  Worst case: O(n²) — if elements arrive in sorted order (tree becomes a
  linked list). Same pathology as quicksort with first-element pivot.

  Self-balancing BSTs (AVL trees, red-black trees) guarantee O(n log n),
  but with higher constant factors due to rotation overhead.

  In practice, tree sort is rare for general sorting — quicksort and merge
  sort are faster. But BSTs are critical data structures for:
    • Ordered maps and sets (C++ std::map, Java TreeMap)
    • Database indexes (B-trees)
    • Interval trees, segment trees (computational geometry)
""")


class BSTNode:
    __slots__ = ['val', 'left', 'right']
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def tree_sort(arr):
    """Sort by inserting into a BST, then in-order traversal."""
    if not arr:
        return [], 0

    comparisons = [0]

    def insert(root, val):
        comparisons[0] += 1
        if root is None:
            return BSTNode(val)
        if val < root.val:
            root.left = insert(root.left, val)
        else:
            root.right = insert(root.right, val)
        return root

    def inorder(node, result):
        if node:
            inorder(node.left, result)
            result.append(node.val)
            inorder(node.right, result)

    root = None
    for val in arr:
        root = insert(root, val)

    result = []
    inorder(root, result)
    return result, comparisons[0]


demo = [5, 3, 8, 1, 9, 2, 7, 4, 6]
print(f"  Input: {demo}")
result, comps = tree_sort(demo)
print(f"  Sorted: {result}")
print(f"  Comparisons: {comps}")
print()

# Show the pathological case
sorted_data = list(range(1, 10))
_, comps_sorted = tree_sort(sorted_data)
random_data = [5, 3, 8, 1, 9, 2, 7, 4, 6]
_, comps_random = tree_sort(random_data)
print(f"  Random input: {comps_random} comparisons (balanced tree)")
print(f"  Sorted input: {comps_sorted} comparisons (degenerate tree = linked list!)")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  HEAPSORT BENCHMARK
# ─────────────────────────────────────────────────────────────────────────────

section("HEAPSORT BENCHMARK — THE GUARANTOR")

print("""\
  Heapsort's killer feature: O(n log n) guaranteed with O(1) extra space.
  Let's see how it performs against merge sort and quicksort on different
  input patterns.
""")


def heapsort(arr):
    """Standard heapsort."""
    arr = arr[:]
    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):
        _sift_down_hs(arr, n, i)
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        _sift_down_hs(arr, i, 0)
    return arr


def _sift_down_hs(arr, n, i):
    while True:
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        if left < n and arr[left] > arr[largest]:
            largest = left
        if right < n and arr[right] > arr[largest]:
            largest = right
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            i = largest
        else:
            break


def merge_sort_basic(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort_basic(arr[:mid])
    right = merge_sort_basic(arr[mid:])
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


def quicksort_basic(arr):
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


n = 50000

print(f"  n = {n:,}")
print()
print(f"  {'Pattern':>16s}  {'Heapsort':>10s}  {'Merge Sort':>10s}  {'Quicksort':>10s}  {'Python':>10s}")
print(f"  {'─'*16}  {'─'*10}  {'─'*10}  {'─'*10}  {'─'*10}")

random.seed(42)
patterns = [
    ("Random",        random.sample(range(n * 10), n)),
    ("Sorted",        list(range(n))),
    ("Reversed",      list(range(n, 0, -1))),
    ("Few unique",    [random.randint(0, 9) for _ in range(n)]),
    ("Nearly sorted", sorted(range(n))),
]
# Slightly perturb "nearly sorted"
nearly = patterns[4][1][:]
for _ in range(n // 100):
    i, j = random.randint(0, n-1), random.randint(0, n-1)
    nearly[i], nearly[j] = nearly[j], nearly[i]
patterns[4] = ("Nearly sorted", nearly)

for label, data in patterns:
    t0 = time.perf_counter()
    heapsort(data)
    t_heap = time.perf_counter() - t0

    t0 = time.perf_counter()
    merge_sort_basic(data)
    t_merge = time.perf_counter() - t0

    t0 = time.perf_counter()
    quicksort_basic(data)
    t_quick = time.perf_counter() - t0

    d = data[:]
    t0 = time.perf_counter()
    d.sort()
    t_py = time.perf_counter() - t0

    print(f"  {label:>16s}  {t_heap:>9.4f}s  {t_merge:>9.4f}s  {t_quick:>9.4f}s  {t_py:>9.4f}s")

print()
print("  Observations:")
print("  • Heapsort: rock-steady performance regardless of input pattern")
print("  • Quicksort: fastest on random data, but sensitive to patterns")
print("  • Merge sort: consistent but uses more memory")
print("  • Python sort: Timsort dominates (C implementation + adaptive strategy)")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  THE k SMALLEST ELEMENTS: PARTIAL SORTING
# ─────────────────────────────────────────────────────────────────────────────

section("PARTIAL SORTING — Finding the k Smallest")

print("""\
  Sometimes you don't need to sort the whole array. You just need the top k.

  • Sort everything, take first k:  O(n log n)
  • Build a min-heap, extract k:    O(n + k log n) ← faster when k << n
  • Build a max-heap of size k:     O(n log k) ← even better for streaming

  The max-heap approach: maintain a heap of the k smallest elements seen
  so far. For each new element: if it's smaller than the heap's max,
  replace the max and sift down. At the end, the heap has the k smallest.

  This is how top-k queries work in databases and search engines.
""")

random.seed(42)
n = 100000
k = 10
data = random.sample(range(n * 100), n)

# Method 1: full sort
t0 = time.perf_counter()
sorted_data = sorted(data)
top_k_full = sorted_data[:k]
t_full = time.perf_counter() - t0

# Method 2: min-heap
import heapq
t0 = time.perf_counter()
top_k_heap = heapq.nsmallest(k, data)
t_heap = time.perf_counter() - t0

print(f"  n = {n:,}, k = {k}")
print(f"  Full sort then slice:  {t_full:.4f}s  → {top_k_full}")
print(f"  heapq.nsmallest:       {t_heap:.4f}s  → {top_k_heap}")
print(f"  Same result? {top_k_full == top_k_heap} ✓")
print()
print(f"  When k is small relative to n, partial sorting is a massive win.")
print()


# ─────────────────────────────────────────────────────────────────────────────
#  SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

section("HEAPS AND TREES: SUMMARY")

print("""\
  ┌─────────────────┬──────────┬──────────┬──────────┬────────┬────────┐
  │ Algorithm       │  Best    │ Average  │  Worst   │ Memory │ Stable │
  ├─────────────────┼──────────┼──────────┼──────────┼────────┼────────┤
  │ Heapsort        │O(n lg n) │O(n lg n) │O(n lg n) │  O(1)  │  No    │
  │ Tournament Sort │O(n lg n) │O(n lg n) │O(n lg n) │  O(n)  │  Yes*  │
  │ Tree Sort (BST) │O(n lg n) │O(n lg n) │  O(n²)   │  O(n)  │  No    │
  │ Tree Sort (AVL) │O(n lg n) │O(n lg n) │O(n lg n) │  O(n)  │  No    │
  └─────────────────┴──────────┴──────────┴──────────┴────────┴────────┘

  * Tournament sort is stable if ties are broken by position.

  Key insight: A heap is more than a sorting trick. It's a priority queue —
  a fundamental data structure that enables Dijkstra's algorithm, event
  simulation, Huffman coding, and countless other algorithms.

  The structure of the data — the implicit tree in the array — IS the
  algorithm. That's the lesson of this script: sometimes the best way to
  sort is to organize the data so that order falls out naturally.

  Next up: breaking the comparison barrier entirely.
""")

print("  ─── End of Script 03 ───")
print()
