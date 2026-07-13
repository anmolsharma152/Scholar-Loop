---
difficulty: easy
last_sent: null
review_count: 0
sequence: 10
tags:
- queue
- deque
topic: dsa
---

# Queue

A queue is a **FIFO (First In, First Out)** data structure. Elements are added at the back and removed from the front. It's used in BFS, task scheduling, buffering, and sliding window maximum problems.

## Core operations

| Operation | Time | Description |
|-----------|------|-------------|
| enqueue | O(1)* | Add to back |
| dequeue | O(1)* | Remove from front |
| peek/front | O(1) | View front without removing |
| isEmpty | O(1) | Check if empty |
| size | O(1) | Number of elements |

*Amortized for array-based implementation.

## Array-based queue (Python collections.deque)

```python
from collections import deque

queue = deque()
queue.append(1)       # enqueue — O(1)
queue.append(2)
front = queue.popleft()  # dequeue — O(1)
```

Python's `list.pop(0)` is O(n) because it shifts all elements. Always use `deque` for queues.

## Circular queue (array-based)

Uses a fixed-size array with head and tail pointers that wrap around. Good for bounded buffer scenarios.

```python
class CircularQueue:
    def __init__(self, capacity):
        self.arr = [None] * capacity
        self.head = 0
        self.tail = 0
        self.size = 0
        self.capacity = capacity

    def enqueue(self, x):
        if self.size == self.capacity:
            raise Exception("Queue is full")
        self.arr[self.tail] = x
        self.tail = (self.tail + 1) % self.capacity
        self.size += 1

    def dequeue(self):
        if self.size == 0:
            raise Exception("Queue is empty")
        val = self.arr[self.head]
        self.head = (self.head + 1) % self.capacity
        self.size -= 1
        return val

    def is_empty(self):
        return self.size == 0
```

## Linked list queue

```python
class Node:
    def __init__(self, val, nxt=None):
        self.val = val
        self.next = nxt

class LinkedQueue:
    def __init__(self):
        self.head = None  # dequeue from here
        self.tail = None  # enqueue here
        self.size = 0

    def enqueue(self, x):
        node = Node(x)
        if self.tail:
            self.tail.next = node
        else:
            self.head = node
        self.tail = node
        self.size += 1

    def dequeue(self):
        if not self.head:
            raise Exception("Queue is empty")
        val = self.head.val
        self.head = self.head.next
        if not self.head:
            self.tail = None
        self.size -= 1
        return val
```

## Deque (double-ended queue)

Supports O(1) insert and remove at **both ends**. Python's `deque` is a deque by default.

```python
from collections import deque

dq = deque()
dq.append(1)          # add to right — O(1)
dq.appendleft(2)      # add to left — O(1)
dq.pop()              # remove from right — O(1)
dq.popleft()          # remove from left — O(1)
```

## Sliding window maximum (deque pattern)

Maintain a deque of indices in decreasing order of values. The front always holds the max for the current window.

```python
from collections import deque

def max_sliding_window(nums, k):
    dq = deque()  # stores indices
    result = []
    for i in range(len(nums)):
        while dq and dq[0] < i - k + 1:
            dq.popleft()  # remove out-of-window
        while dq and nums[dq[-1]] <= nums[i]:
            dq.pop()  # remove smaller elements
        dq.append(i)
        if i >= k - 1:
            result.append(nums[dq[0]])
    return result
```

## BFS using queue

```python
from collections import deque

def bfs(graph, start):
    visited = {start}
    queue = deque([start])
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order
```

## Queue using two stacks

```python
class QueueFromStacks:
    def __init__(self):
        self.inbox = []
        self.outbox = []

    def enqueue(self, x):
        self.inbox.append(x)

    def dequeue(self):
        if not self.outbox:
            while self.inbox:
                self.outbox.append(self.inbox.pop())
        return self.outbox.pop()
```

Each element is moved at most once between stacks, giving amortized O(1) per operation.

## Common bugs

- Using `list.pop(0)` instead of `deque.popleft()` — O(n) vs O(1)
- Forgetting that dequeue modifies the original collection
- Infinite loop in BFS when not tracking visited nodes
- Off-by-one in circular queue: using `tail + 1` instead of `(tail + 1) % capacity`

## Time/space

- deque operations: **O(1)** all
- Circular queue: **O(1)** all, **O(k)** space where k is capacity
- Sliding window max: **O(n)** time, **O(k)** space
- BFS: **O(V + E)** time, **O(V)** space