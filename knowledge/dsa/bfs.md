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

Traverses a graph **level by level** using a **queue**. Explores all neighbors of a node before moving to the next level. Naturally finds the **shortest path** in an unweighted graph.

## Algorithm

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

## When to use BFS

| Problem | Why BFS |
|---------|---------|
| Shortest path in unweighted graph | BFS guarantees min edges first |
| Level-order tree traversal | Process by depth |
| Word ladder | Transform string → string, BFS on state space |
| Min steps / moves | Each move is one edge; BFS finds min steps |
| Bipartite check | Alternate colors by level |

## Common bugs

- Using a stack instead of a queue (that's DFS)
- Forgetting to mark visited **when enqueuing**, not when dequeuing (avoids duplicates)
- Not handling disconnected components / nodes
- Not tracking distance / parent separately

## Time/space

- Time: **O(V + E)** — each vertex and edge visited once
- Space: **O(V)** — queue and visited set