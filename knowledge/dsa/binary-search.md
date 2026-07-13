---
difficulty: medium
last_sent: null
review_count: 0
sequence: 5
tags:
- searching
- binary-search
topic: dsa
---

# Binary Search

Binary search finds a target in a **sorted collection** by repeatedly halving the search space. It's the poster child for O(log n) algorithms and appears in many disguised forms — not just "find x in array."

## The core pattern

Always maintain the invariant: the answer is in `[lo, hi]`. Each iteration narrows the range by half.

```python
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2  # avoid overflow
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```

## Lower and upper bound

Find the **first** position where a condition becomes true — this is the real power of binary search.

```python
def lower_bound(arr, target):
    """First index where arr[i] >= target."""
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo

def upper_bound(arr, target):
    """First index where arr[i] > target."""
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo
```

## Binary search on answer space

Many problems don't have a sorted array but the **answer itself** can be binary searched. Check if a candidate answer is feasible in O(n), then narrow the range.

```python
def min_ship_capacity(weights, days):
    """Minimum capacity to ship all weights within `days` days."""
    def can_ship(capacity):
        used_days = 1
        current = 0
        for w in weights:
            if current + w > capacity:
                used_days += 1
                current = w
            else:
                current += w
        return used_days <= days

    lo = max(weights)          # must carry heaviest item
    hi = sum(weights)          # carry everything in one day
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if can_ship(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
```

## Peak element (binary search on unsorted array)

```python
def find_peak(arr):
    lo, hi = 0, len(arr) - 1
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] < arr[mid + 1]:
            lo = mid + 1
        else:
            hi = mid
    return lo
```

## Ternary search concept

Used to find the maximum/minimum of a **unimodal** function (increases then decreases). Divides the range into thirds instead of halves.

```python
def ternary_search(f, lo, hi, eps=1e-9):
    while hi - lo > eps:
        m1 = lo + (hi - lo) / 3
        m2 = hi - (hi - lo) / 3
        if f(m1) < f(m2):
            lo = m1
        else:
            hi = m2
    return (lo + hi) / 2
```

Ternary search is O(log_{1.5}(range/eps)) — less common than binary search but useful for optimization problems on continuous domains.

## Common bugs

- Using `mid = (lo + hi) // 2` causes overflow in some languages — use `lo + (hi - lo) // 2`
- Infinite loop when `lo = mid` and `mid` never changes — always use `mid + 1` or `mid - 1`
- Wrong boundary: `lo <= hi` for exact search, `lo < hi` for lower/upper bound
- Applying binary search to unsorted data without a monotonic predicate
- Forgetting that Python integers don't overflow (so `lo + hi` is fine here)

## Time/space

- Time: **O(log n)** per search
- Space: **O(1)** iterative, **O(log n)** recursive
- Binary search on answer: **O(n log R)** where R is the answer range