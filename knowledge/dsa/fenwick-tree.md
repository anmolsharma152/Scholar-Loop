---
difficulty: hard
last_sent: null
review_count: 0
sequence: 19
tags:
- fenwick-tree
- bit
- range-query
topic: dsa
---

# Fenwick tree (Binary Indexed Tree)

A data structure that efficiently maintains **prefix sums** of an array with **point updates**. Both operations are O(log n). The key insight: each index `i` is responsible for a range of length `i & -i` (the lowest set bit). Simpler than a segment tree but limited to operations that are **invertible** (sum, xor, mul) — not min/max.

## Implementation

```python
class Fenwick:
    def __init__(self, n):
        self.n = n
        self.tree = [0] * (n + 1)  # 1-indexed

    def add(self, idx, delta):
        """Add delta at position idx (1-indexed)."""
        while idx <= self.n:
            self.tree[idx] += delta
            idx += idx & -idx

    def sum(self, idx):
        """Prefix sum [1..idx]."""
        res = 0
        while idx > 0:
            res += self.tree[idx]
            idx -= idx & -idx
        return res

    def range_sum(self, l, r):
        """Sum on [l..r] (1-indexed)."""
        return self.sum(r) - self.sum(l - 1)
```

## Building from an array

Instead of calling `add` n times (O(n log n)), build in O(n):

```python
def build(nums):
    n = len(nums)
    tree = [0] + nums[:]
    for i in range(1, n + 1):
        j = i + (i & -i)
        if j <= n:
            tree[j] += tree[i]
    return tree
```

## Classic problems

| Problem | Variant |
|---------|---------|
| Range sum query | Point update + prefix sum |
| Count of smaller numbers after self | BIT over compressed values, traverse right-to-left |
| Reverse pairs | BIT over compressed values |
| Number of subarrays with bounded maximum | BIT of indices |
| Longest increasing subsequence (O(n log n)) | BIT over compressed values, DP on max length up to value |

## Common bugs

- 0-index vs 1-index confusion — BIT is naturally 1-indexed
- `idx & -idx` gives the lowest set bit, not clearing it
- Using BIT for range updates without the difference-array trick
- Forgetting that BIT cannot do range min/max queries (not invertible)

## BIT vs segment tree

| BIT | Segment tree |
|-----|-------------|
| Simple, low constant | More flexible |
| Prefix sums only | Any associative operation |
| O(log n) per op | O(log n) per op |
| ~3× faster in practice | Supports range updates + lazy |

## Time/space

- Time: **O(log n)** per add and sum (build is O(n))
- Space: **O(n)** — the tree array of size n+1