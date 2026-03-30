# Sorting: From Bubbles to Parallel Machines

**How computers put things in order — from the simplest swaps to algorithms that power Python, Java, and Google.**

Sorting is the most studied problem in computer science. It's also the most practical — every database query, every search result, every spreadsheet column relies on it. This repository walks through the full story: from the quadratic naivety of bubble sort to the industry-grade sophistication of Timsort, from counting sort's clever trick to bitonic sort's parallel beauty, and from Bill Gates' pancake problem to quantum bogosort's existential dread.

Each script is self-contained, narrative-driven, and meant to be **read as much as run**. The code IS the textbook.

---

## Scripts

| # | File | Topic | Key Algorithms |
|---|------|-------|---------------|
| 01 | [`01_the_naive_sorts.py`](01_the_naive_sorts.py) | **Why Order Matters** | Bubble sort, cocktail shaker, selection sort, insertion sort, binary insertion sort |
| 02 | [`02_divide_and_conquer.py`](02_divide_and_conquer.py) | **Breaking the Quadratic Wall** | Merge sort, quicksort (Lomuto/Hoare), median-of-3, 3-way quicksort, Master Theorem |
| 03 | [`03_heaps_and_trees.py`](03_heaps_and_trees.py) | **Structure-Based Sorting** | Binary heaps, heapsort, priority queues, tournament sort, tree sort |
| 04 | [`04_beyond_comparison.py`](04_beyond_comparison.py) | **Breaking the n·log·n Barrier** | Counting sort, radix sort (LSD/MSD), bucket sort, decision tree lower bound |
| 05 | [`05_adaptive_and_hybrid.py`](05_adaptive_and_hybrid.py) | **Exploiting Existing Order** | Timsort, galloping mode, introsort, Shellsort, natural merge sort |
| 06 | [`06_parallel_and_network_sorts.py`](06_parallel_and_network_sorts.py) | **Sorting When You Have Friends** | Sorting networks, bitonic sort, odd-even merge, external sort, MapReduce |
| 07 | [`07_exotic_and_theoretical.py`](07_exotic_and_theoretical.py) | **The Wild Ones** | Bogosort, slowsort, sleep sort, spaghetti sort, pancake sort, bead sort, Stalin sort |
| 08 | [`08_the_great_sort_off.py`](08_the_great_sort_off.py) | **The Capstone** | All algorithms benchmarked, scaling analysis, stability matrix, the algorithm selector |
| 09 | [`09_bitwise_and_novel_sorts.py`](09_bitwise_and_novel_sorts.py) | **Bitwise Alchemy** | Radix exchange, bit-parallel gravity, Newton's estimate sort, wavelet tree sort, CA sort, Morton sort |

## Interactive Visualizer

Open [`sort_explorer.html`](sort_explorer.html) in any browser — zero dependencies, zero build step.

- **13 algorithms** with real-time visualization
- **Sound mode** — hear the sort (Web Audio API)
- **Race mode** — pit two algorithms head-to-head
- **8 data patterns** — random, nearly sorted, reversed, pipe organ, sawtooth, sinusoidal, few unique, already sorted
- **4 color schemes** — rainbow (sorted position), heat map, mono, neon
- **Step-through mode** — advance one operation at a time
- **Live stats** — comparisons, swaps, array accesses, elapsed time
- **Chaos meter** — watch disorder decrease in real time
- **Confetti** — because sorting deserves celebration

## Running

```bash
# Any script, standalone
python3 01_the_naive_sorts.py

# Run them all in order
for f in 0*.py; do python3 "$f"; done

# Interactive visualizer
open sort_explorer.html        # macOS
xdg-open sort_explorer.html   # Linux
```

**Requirements:** Python 3.10+ · No dependencies (pure stdlib)

## The Complexity Cheat Sheet

```
┌──────────────────┬──────────┬──────────┬──────────┬────────┬────────┐
│ Algorithm        │  Best    │ Average  │  Worst   │ Memory │ Stable │
├──────────────────┼──────────┼──────────┼──────────┼────────┼────────┤
│ Bubble sort      │  O(n)    │  O(n²)   │  O(n²)   │  O(1)  │  Yes   │
│ Insertion sort   │  O(n)    │  O(n²)   │  O(n²)   │  O(1)  │  Yes   │
│ Selection sort   │  O(n²)   │  O(n²)   │  O(n²)   │  O(1)  │  No    │
│ Merge sort       │O(n lg n) │O(n lg n) │O(n lg n) │  O(n)  │  Yes   │
│ Quicksort        │O(n lg n) │O(n lg n) │  O(n²)   │O(lg n) │  No    │
│ Heapsort         │O(n lg n) │O(n lg n) │O(n lg n) │  O(1)  │  No    │
│ Counting sort    │ O(n+k)   │ O(n+k)   │ O(n+k)   │ O(n+k) │  Yes   │
│ Radix sort (LSD) │ O(d·n)   │ O(d·n)   │ O(d·n)   │ O(n+b) │  Yes   │
│ Timsort          │  O(n)    │O(n lg n) │O(n lg n) │  O(n)  │  Yes   │
│ Introsort        │O(n lg n) │O(n lg n) │O(n lg n) │O(lg n) │  No    │
│ Shellsort        │O(n lg n) │ varies   │ varies   │  O(1)  │  No    │
│ Bitonic sort     │O(nlog²n) │O(nlog²n) │O(nlog²n) │  O(1)  │  No    │
├──────────────────┼──────────┼──────────┼──────────┼────────┼────────┤
│ Radix exchange   │ O(b·n)   │ O(b·n)   │ O(b·n)   │  O(b)  │  No    │
│ Wavelet tree     │O(nlog σ) │O(nlog σ) │O(nlog σ) │O(nlogσ)│  Yes   │
│ CA sort (par.)   │  O(n)    │  O(n)    │  O(n)    │  O(1)  │  Yes   │
└──────────────────┴──────────┴──────────┴──────────┴────────┴────────┘
```

## Connection Map

This is repository **7** in the series:

```
[1] periodic-table              ← element data structures
[2] navigational-pathfinding    ← graphs, Dijkstra (→ heaps, script 03)
[3] number-systems              ← bases, digits (→ radix sort, script 04)
[4] bit-tricks-and-wave-funcs   ← binary operations (→ radix exchange, gravity, Morton, script 09)
[5] waveguides                  ← signal processing (→ wavelet tree sort, script 09)
[6] fisr-to-conway-and-beyond   ← algorithms, computation (→ Newton's estimate, CA sort, script 09)
[7] sorting ← YOU ARE HERE
```

## License

MIT — see [LICENSE](LICENSE)
