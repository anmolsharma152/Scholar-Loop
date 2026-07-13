---
difficulty: medium
last_sent: null
review_count: 0
tags:
  - divide-and-conquer
topic: dsa
---

# Divide and conquer

A paradigm that splits a problem into **smaller subproblems**, solves each **recursively**, then **combines** the results. The base case is trivial (size 0 or 1). Works well when subproblems are independent and the combine step is efficient.

## Merge sort

Divide array into halves, recursively sort, merge two sorted halves in O(n).

```python
def merge_sort(nums):
    if len(nums) <= 1:
        return nums
    mid = len(nums) // 2
    left = merge_sort(nums[:mid])
    right = merge_sort(nums[mid:])
    return merge(left, right)

def merge(a, b):
    i = j = 0
    res = []
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            res.append(a[i])
            i += 1
        else:
            res.append(b[j])
            j += 1
    res.extend(a[i:])
    res.extend(b[j:])
    return res
```

## Quick sort

Pick a pivot, partition around it, recursively sort both sides. In-place version:

```python
def quick_sort(nums, lo=0, hi=None):
    if hi is None:
        hi = len(nums) - 1
    if lo < hi:
        p = partition(nums, lo, hi)
        quick_sort(nums, lo, p - 1)
        quick_sort(nums, p + 1, hi)

def partition(nums, lo, hi):
    pivot = nums[hi]
    i = lo
    for j in range(lo, hi):
        if nums[j] <= pivot:
            nums[i], nums[j] = nums[j], nums[i]
            i += 1
    nums[i], nums[hi] = nums[hi], nums[i]
    return i
```

## Classic problems

| Problem | How divide-and-conquer applies |
|---------|-------------------------------|
| Closest pair of points | Divide by x-mid, recurse, combine with strip of width 2δ |
| Strassen's matrix multiplication | 7 recursive multiplications instead of 8 (O(n²·⁸¹) vs O(n³)) |
| Maximum subarray (Kadane's DC) | Split array; max crosses the midpoint |
| Count inversions | Modified merge sort: count when left[i] > right[j] |
| Pow(x, n) | Divide exponent by 2, handle odd case |
| The skyline problem | Merge two skylines by x-coordinate |

## Mental model

1. **Divide**: Split the problem into smaller instances of the same problem
2. **Conquer**: Solve each subproblem recursively
3. **Combine**: Merge the partial solutions into the final answer

The combine step is usually where the real logic lives. In merge sort it's merging; in closest pairs it's the strip check.

## Common bugs

- Forgetting the base case (infinite recursion)
- Stack overflow on large inputs — iterative or tail-call optimization for quicksort
- Quick sort: worst-case O(n²) on already-sorted arrays (use random pivot)
- Merge sort: O(n) extra space for the merge (it's not in-place)
- Modify-and-recurse vs copy-and-recurse confusion

## Time/space

| Algorithm | Time | Space |
|-----------|------|-------|
| Merge sort | **O(n log n)** | **O(n)** |
| Quick sort | **O(n log n)** avg, **O(n²)** worst | **O(log n)** (stack) |
| Closest pair | **O(n log n)** | **O(n)** |
| Strassen's | **O(n²·⁸¹)** | **O(n²)** |
