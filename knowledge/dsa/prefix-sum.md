---
difficulty: easy
last_sent: null
review_count: 0
tags:
- prefix-sum
- arrays
topic: dsa
---

# Prefix Sum

Prefix sum is a technique that **precomputes cumulative sums** so that range sum queries can be answered in O(1). Instead of recalculating the sum of a subarray every time, you build a prefix array once and use subtraction. This is one of the most versatile precomputation tricks.

## The core idea

For array `a`, build prefix array `p` where `p[i] = a[0] + a[1] + ... + a[i-1]`.

Then the sum of subarray `a[i..j]` (inclusive) is simply `p[j+1] - p[i]`.

```python
def build_prefix(arr):
    prefix = [0] * (len(arr) + 1)
    for i in range(len(arr)):
        prefix[i + 1] = prefix[i] + arr[i]
    return prefix

def range_sum(prefix, i, j):
    return prefix[j + 1] - prefix[i]
```

## 2D prefix sum

For a matrix, compute a 2D prefix sum to answer rectangle sum queries in O(1).

```python
def build_prefix_2d(matrix):
    m, n = len(matrix), len(matrix[0])
    prefix = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m):
        for j in range(n):
            prefix[i+1][j+1] = (
                matrix[i][j]
                + prefix[i][j+1]
                + prefix[i+1][j]
                - prefix[i][j]  # subtract overlap
            )
    return prefix

def rect_sum(prefix, r1, c1, r2, c2):
    """Sum of rectangle from (r1,c1) to (r2,c2) inclusive."""
    return (
        prefix[r2+1][c2+1]
        - prefix[r1][c2+1]
        - prefix[r2+1][c1]
        + prefix[r1][c1]
    )
```

## Difference arrays

A difference array lets you apply **range updates in O(1)**, then compute final values with a single prefix sum pass.

```python
def apply_range_update(n, updates):
    """updates = [(l, r, val), ...] — add val to arr[l..r]."""
    diff = [0] * (n + 1)
    for l, r, val in updates:
        diff[l] += val
        diff[r + 1] -= val
    # Reconstruct final array
    result = [0] * n
    result[0] = diff[0]
    for i in range(1, n):
        result[i] = result[i - 1] + diff[i]
    return result
```

## Subarray sum equals K

Count subarrays whose sum equals `k` using prefix sums and a hash map.

```python
def subarray_sum(nums, k):
    count = 0
    prefix_sum = 0
    seen = {0: 1}
    for x in nums:
        prefix_sum += x
        if prefix_sum - k in seen:
            count += seen[prefix_sum - k]
        seen[prefix_sum] = seen.get(prefix_sum, 0) + 1
    return count
```

## Running XOR (prefix XOR)

Same idea works with XOR for range XOR queries and "find missing number" problems.

```python
def prefix_xor(arr):
    prefix = [0] * (len(arr) + 1)
    for i in range(len(arr)):
        prefix[i + 1] = prefix[i] ^ arr[i]
    return prefix
```

## Common bugs

- Off-by-one in prefix array sizing: prefix has `n+1` elements, not `n`
- Forgetting the `+1` offset when querying: `sum(i..j) = prefix[j+1] - prefix[i]`
- In 2D prefix sum, forgetting to add back the subtracted overlap
- Using prefix sum for non-invertible operations (it only works where you can "undo" via subtraction/XOR)
- Integer overflow with large prefix sums (not an issue in Python)

## Time/space

- Build prefix array: **O(n)** time, **O(n)** space
- Range sum query: **O(1)** time
- 2D build: **O(m×n)** time, **O(m×n)** space
- 2D query: **O(1)** time
- Difference array update: **O(1)** per update, **O(n)** to reconstruct
