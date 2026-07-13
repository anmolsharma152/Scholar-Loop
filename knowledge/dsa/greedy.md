---
difficulty: medium
last_sent: null
review_count: 0
tags:
  - greedy
topic: dsa
---

# Greedy algorithms

Make the **locally optimal choice** at each step, hoping it leads to a globally optimal solution. Greedy works when a problem has **optimal substructure** and the **greedy choice property** (a global optimum can be reached by making local optima).

## When greedy works

| Property | Meaning |
|----------|---------|
| **Greedy choice property** | A globally optimal solution begins with a locally optimal choice |
| **Optimal substructure** | An optimal solution contains optimal solutions to subproblems |
| **Matroid / matroid-like structure** | Problems like MST, Huffman coding have this property |

Greedy does **not** always work (e.g., 0/1 knapsack does not have the greedy choice property; fractional knapsack does).

## Activity selection

```python
def max_activities(activities):
    activities.sort(key=lambda x: x[1])  # sort by end time
    count = 1
    last_end = activities[0][1]
    for start, end in activities[1:]:
        if start >= last_end:
            count += 1
            last_end = end
    return count
```

## Huffman coding (concept)

Build a **prefix-free** binary code from character frequencies. Repeatedly merge the two least-frequent nodes into a tree. The resulting code has minimum weighted path length.

```python
import heapq

def huffman(freq):
    heap = [[w, [c, ""]] for c, w in freq.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)
        for pair in lo[1:]: pair[1] = "0" + pair[1]
        for pair in hi[1:]: pair[1] = "1" + pair[1]
        heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
    return heap[0][1:]  # list of (char, code)
```

## Classic problems

| Problem | Greedy strategy |
|---------|----------------|
| Activity selection | Pick earliest finish |
| Fractional knapsack | Highest value/weight ratio first |
| Coin change (canonical) | Largest coin first |
| Minimum spanning tree | Prim / Kruskal |
| Dijkstra (shortest path) | Closest unvisited vertex first |
| Jump game | Max reachable index at each step |

## Common bugs

- Applying greedy when the problem does not have the greedy choice property
- Not proving (or at least testing) that greedy works for the specific problem
- Missing edge cases where tie-breaking matters
- Assuming sorted input when it isn't

## Time/space

- Time: **O(n log n)** typically (sorting dominates)
- Space: **O(1)** or **O(n)** depending on sorting
