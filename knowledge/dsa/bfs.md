---
difficulty: medium
last_sent: null
review_count: 0
sequence: 16
tags:
- graphs
- bfs
topic: dsa
---

# Breadth-first search (BFS)

Traverses a graph **level by level** using a **queue**. Explores all neighbors of a node before moving to the next level. Naturally finds the **shortest path** in an unweighted graph because it explores nodes in order of their distance from the source.

## Algorithm

BFS explores all neighbors of the current node before moving to the next level. It uses a queue (FIFO) to ensure level-by-level traversal. Mark nodes as visited when enqueuing to avoid duplicates.

```python
from collections import deque

def bfs(graph, start):
    visited = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        print(node)  # process
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
```

## Shortest path (unweighted)

```python
def shortest_path(graph, start, target):
    visited = {start}
    queue = deque([(start, 0)])  # (node, distance)
    while queue:
        node, dist = queue.popleft()
        if node == target: return dist
        for nbr in graph[node]:
            if nbr not in visited:
                visited.add(nbr)
                queue.append((nbr, dist + 1))
    return -1
```

This works because BFS explores nodes in order of distance — the first time we reach `target`, it's guaranteed to be the shortest path. For weighted graphs, use Dijkstra's algorithm instead.

## When to use BFS

| Problem | Why BFS |
|---------|---------|
| Shortest path in unweighted graph | BFS guarantees min edges first |
| Level-order tree traversal | Process by depth |
| Word ladder | Transform string → string, BFS on state space |
| Min steps / moves | Each move is one edge; BFS finds min steps |
| Bipartite check | Alternate colors by level |

## BFS vs DFS

## Common bugs

- Using a stack instead of a queue (that's DFS) — stack LIFO vs queue FIFO changes traversal order
- Forgetting to mark visited **when enqueuing**, not when dequeuing — causes duplicate entries in queue
- Not handling disconnected components / nodes — run BFS from each unvisited node
- Not tracking distance / parent separately — store them alongside the node in the queue

## Time/space

- Time: **O(V + E)** — each vertex and edge visited once
- Space: **O(V)** — queue and visited set can hold all vertices in worst case

## Template

```python
from collections import deque

def bfs(graph, start):
    visited = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        # process node here
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
```