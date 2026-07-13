---
difficulty: hard
last_sent: null
review_count: 0
tags:
  - segment-tree
  - range-query
topic: dsa
---

# Segment tree

A tree data structure that stores intervals or segments. Enables **range queries** (sum, min, max, gcd) and **point updates** in O(log n). Each leaf represents an array element; each internal node represents the result of its children. Can be extended to **range updates** with lazy propagation.

## Array-based implementation (range sum)

```python
class SegmentTree:
    def __init__(self, nums):
        n = len(nums)
        self.n = n
        self.tree = [0] * (2 * n)
        # build: leaves in second half
        for i in range(n):
            self.tree[n + i] = nums[i]
        for i in range(n - 1, 0, -1):
            self.tree[i] = self.tree[2 * i] + self.tree[2 * i + 1]

    def update(self, index, val):
        pos = index + self.n
        self.tree[pos] = val
        pos //= 2
        while pos:
            self.tree[pos] = self.tree[2 * pos] + self.tree[2 * pos + 1]
            pos //= 2

    def query(self, left, right):
        # range [left, right) — half-open
        l, r = left + self.n, right + self.n
        res = 0
        while l < r:
            if l % 2:
                res += self.tree[l]
                l += 1
            if r % 2:
                r -= 1
                res += self.tree[r]
            l //= 2
            r //= 2
        return res
```

## Lazy propagation (range update)

Store pending updates in a `lazy` array. Delay applying them until a query or update actually visits a node. Without lazy, range updates become O(n log n) instead of O(log n).

## Classic problems

| Problem | Variant |
|---------|---------|
| Range sum query | Point update + range sum |
| Range minimum query | Min over range, point or range update |
| Count of smaller numbers after self | Coordinate compress + seg tree of frequencies |
| My calendar I / II | Segment tree with range max and lazy |
| Falling squares | Coordinate compress + range max + lazy |
| Range module | Segment tree with boolean coverage + lazy |

## Common bugs

- Off-by-one with half-open [l, r) vs closed [l, r] intervals
- Not allocating enough space (2 × next power of two, or 4 × n for recursive tree)
- Mixing up left/right child indexing (2*i, 2*i+1)
- Forgetting to propagate lazy values before recursing in queries

## Time/space

- Time: **O(log n)** per query and update (build is O(n))
- Space: **O(n)** — the tree array of size 2n (or 4n for recursive)
