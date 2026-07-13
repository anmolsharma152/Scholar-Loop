---
difficulty: medium
last_sent: null
review_count: 0
tags:
  - heap
  - priority-queue
topic: dsa
---

# Heap / priority queue

A **complete binary tree** where every parent is ≤ its children (**min-heap**) or ≥ its children (**max-heap**). Implemented as an array for cache efficiency. A **priority queue** is an abstract data type typically backed by a heap.

## Array representation

```text
index:  0  1  2  3  4  5  6
value: [1, 3, 6, 5, 9, 8]
```

For node at index `i`:
- Parent: `(i - 1) // 2`
- Left child: `2 * i + 1`
- Right child: `2 * i + 2`

## Core operations

```python
import heapq

heap = []                   # Python uses min-heap by default
heapq.heappush(heap, 5)     # O(log n)
heapq.heappop(heap)         # O(log n), returns smallest
heap[0]                     # O(1) peek
heapq.heapify(arr)          # O(n) build heap
```

For max-heap: push `(-x, x)` or negate values.

## Heap sort

```python
def heap_sort(arr):
    heapq.heapify(arr)
    return [heapq.heappop(arr) for _ in range(len(arr))]
```

Time: **O(n log n)**. Space: O(n) if building a new list, O(1) if in-place.

## Classic problems

| Problem | Heap approach |
|---------|---------------|
| Kth largest element | Min-heap of size k |
| Merge K sorted lists | Push (value, list_id, index) onto heap |
| Median from data stream | Two heaps (max-heap for left, min-heap for right) |
| Top K frequent elements | Min-heap of size K by frequency |
| Task scheduler | Max-heap of task counts |

## Common bugs

- Heap property violated when using custom objects; provide a tuple or `__lt__`
- Forgetting that heap pop removes the **smallest** (min-heap), not the largest
- Building heap from empty list by repeated push is O(n log n); prefer `heapify`

## Time/space

- Push / Pop: **O(log n)**
- Peek: **O(1)**
- Build heap: **O(n)**
- Space: **O(n)**
