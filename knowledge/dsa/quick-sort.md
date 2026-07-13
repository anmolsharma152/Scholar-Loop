---
difficulty: medium
last_sent: null
review_count: 0
tags:
- sorting
- divide-and-conquer
topic: dsa
---

# Quick Sort

Quick sort is a **divide-and-conquer** sorting algorithm that picks a pivot, partitions the array around it, and recursively sorts the partitions. It's faster than merge sort in practice due to cache efficiency and smaller constants, but has O(n²) worst case.

## The algorithm

1. **Choose pivot**: Pick an element (first, last, random, or median-of-three)
2. **Partition**: Rearrange so elements < pivot are left, elements > pivot are right
3. **Recurse**: Sort left and right partitions

## Lomuto partition scheme

Simpler to implement. Pivot is the last element. Maintains an index `i` for the boundary of "small elements."

```python
def quicksort(arr, lo=0, hi=None):
    if hi is None:
        hi = len(arr) - 1
    if lo < hi:
        p = lomuto_partition(arr, lo, hi)
        quicksort(arr, lo, p - 1)
        quicksort(arr, p + 1, hi)

def lomuto_partition(arr, lo, hi):
    pivot = arr[hi]
    i = lo
    for j in range(lo, hi):
        if arr[j] <= pivot:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
    arr[i], arr[hi] = arr[hi], arr[i]
    return i
```

## Hoare partition scheme

Uses two pointers moving inward. More efficient — does fewer swaps on average. Pivot is typically the first element.

```python
def quicksort_hoare(arr, lo=0, hi=None):
    if hi is None:
        hi = len(arr) - 1
    if lo < hi:
        p = hoare_partition(arr, lo, hi)
        quicksort_hoare(arr, lo, p)
        quicksort_hoare(arr, p + 1, hi)

def hoare_partition(arr, lo, hi):
    pivot = arr[lo]
    i, j = lo - 1, hi + 1
    while True:
        i += 1
        while arr[i] < pivot:
            i += 1
        j -= 1
        while arr[j] > pivot:
            j -= 1
        if i >= j:
            return j
        arr[i], arr[j] = arr[j], arr[i]
```

## Randomized quicksort

Avoids worst-case by choosing a random pivot. Makes worst case astronomically unlikely.

```python
import random

def randomized_partition(arr, lo, hi):
    rand_idx = random.randint(lo, hi)
    arr[rand_idx], arr[hi] = arr[hi], arr[rand_idx]
    return lomuto_partition(arr, lo, hi)

def quicksort_random(arr, lo=0, hi=None):
    if hi is None:
        hi = len(arr) - 1
    if lo < hi:
        p = randomized_partition(arr, lo, hi)
        quicksort_random(arr, lo, p - 1)
        quicksort_random(arr, p + 1, hi)
```

## Quick select (find k-th smallest)

Uses the partition step without recursing on both sides — O(n) average.

```python
def quickselect(arr, k, lo=0, hi=None):
    """Find k-th smallest element (0-indexed)."""
    if hi is None:
        hi = len(arr) - 1
    if lo == hi:
        return arr[lo]
    p = randomized_partition(arr, lo, hi)
    if k == p:
        return arr[p]
    elif k < p:
        return quickselect(arr, k, lo, p - 1)
    else:
        return quickselect(arr, k, p + 1, hi)
```

## Worst-case analysis

| Scenario | Time | Why |
|----------|------|-----|
| Already sorted + bad pivot | O(n²) | One partition is always empty |
| Random pivot (expected) | O(n log n) | Balanced partitions on average |
| Median-of-three | O(n log n) | Avoids sorted-input trap |

## Tail recursion optimization

Only recurse into the smaller partition and iterate on the larger one — limits stack depth to O(log n).

```python
def quicksort_tail(arr, lo=0, hi=None):
    if hi is None:
        hi = len(arr) - 1
    while lo < hi:
        p = randomized_partition(arr, lo, hi)
        if p - lo < hi - p:
            quicksort_tail(arr, lo, p - 1)
            lo = p + 1
        else:
            quicksort_tail(arr, p + 1, hi)
            hi = p - 1
```

## Common bugs

- Lomuto: choosing last element as pivot on already-sorted array gives O(n²)
- Hoare: forgetting the `i < j` guard causes out-of-bounds access
- Using `<` vs `<=` in partition affects how duplicates are handled
- Not handling empty subarrays (`lo >= hi` base case)
- Stack overflow from deep recursion on pathological inputs (use tail optimization or randomization)

## Time/space

- Time: **O(n log n)** average, **O(n²)** worst (O(n log n) with random pivot expected)
- Space: **O(log n)** stack (tail-optimized), **O(n)** worst case without optimization
- Quick select: **O(n)** average time, **O(1)** space
