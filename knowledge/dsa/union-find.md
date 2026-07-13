---
difficulty: hard
last_sent: null
review_count: 0
sequence: 16
tags:
- graph
- union-find
- dsu
topic: dsa
---

# Union find (Disjoint Set Union)

A data structure that tracks a set of elements partitioned into **disjoint (non-overlapping) subsets**. Supports two operations: `find(x)` — which set does x belong to? — and `union(x, y)` — merge the sets of x and y. With **path compression** and **union by rank/size**, near-constant amortized time per operation (inverse Ackermann function).

## Implementation

```python
class DSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [1] * n          # or self.size = [1] * n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # path compression
            x = self.parent[x]
        return x

    def union(self, x, y):
        xr, yr = self.find(x), self.find(y)
        if xr == yr:
            return False
        # union by rank
        if self.rank[xr] < self.rank[yr]:
            self.parent[xr] = yr
        elif self.rank[xr] > self.rank[yr]:
            self.parent[yr] = xr
        else:
            self.parent[yr] = xr
            self.rank[xr] += 1
        return True
```

## Applications

- **Cycle detection in undirected graphs**: if `union(u, v)` returns `False`, adding (u,v) creates a cycle
- **Number of connected components**: count how many nodes are their own parent after all unions
- **Kruskal's MST**: sort edges by weight, union non-cycle edges until V-1 edges selected
- **Dynamic connectivity**: online queries of whether two nodes are in the same component

## Classic problems

| Problem | Trick |
|---------|-------|
| Number of provinces | Union connected cities; count roots |
| Accounts merge | Union accounts by email; group by root |
| Redundant connection | First edge whose union returns False is the answer |
| Longest consecutive sequence | Union adjacent numbers in one pass |
| Number of islands II | Union adjacent land cells as they're added |

## Common bugs

- Forgetting path compression — leads to O(n) find
- Union by rank but not using it to attach smaller tree under larger tree
- Not calling `find` on both arguments of `union` before comparing roots
- Using union-find on directed graphs (it's for undirected connectivity)

## Time/space

- Time: **O(α(n))** amortized per operation (inverse Ackermann, practically constant)
- Space: **O(n)** — parent and rank/size arrays