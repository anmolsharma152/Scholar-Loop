---
difficulty: medium
last_sent: null
review_count: 0
sequence: 16
tags:
- graphs
- dfs
topic: dsa
---

# Depth-first search (DFS)

Explores a graph by going as **deep as possible** before backtracking. Uses a **stack** (explicit or recursion). Tracks visited nodes to avoid cycles. Three **visit orders** mirror tree traversals: pre-order (visit first), in-order (visit between children), post-order (visit after children).

## Recursive DFS

```python
def dfs_recursive(graph, node, visited):
    visited.add(node)
    print(node)  # pre-order: process when first seen
    for nbr in graph[node]:
        if nbr not in visited:
            dfs_recursive(graph, nbr, visited)
```

## Iterative DFS

```python
def dfs_iterative(graph, start):
    visited = {start}
    stack = [start]
    while stack:
        node = stack.pop()
        print(node)  # pre-order
        for nbr in graph[node]:
            if nbr not in visited:
                visited.add(nbr)
                stack.append(nbr)
```

## Cycle detection

```python
def has_cycle(graph):
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {v: WHITE for v in graph}

    def dfs(u):
        color[u] = GRAY
        for v in graph[u]:
            if color[v] == GRAY: return True  # back edge → cycle
            if color[v] == WHITE and dfs(v): return True
        color[u] = BLACK
        return False

    for v in graph:
        if color[v] == WHITE and dfs(v): return True
    return False
```

## When to use DFS

| Problem | Approach |
|---------|----------|
| Path existence | DFS finds any path (don't need shortest) |
| Connected components | Run DFS from each unvisited node |
| Topological sort | Post-order DFS, then reverse |
| Cycle detection | Track recursion stack (directed) or parent (undirected) |
| Maze solving | DFS with backtracking explores all routes |
| Find all paths | DFS explores every route to find all solutions |

## DFS vs BFS

DFS uses less memory (stack vs queue) and is natural for backtracking problems. BFS guarantees shortest path. Use DFS when you need to explore all possibilities (combinations, permutations, mazes). Use BFS when you need level-order or shortest distance.

## Common bugs

- Stack overflow on deep recursion (use iterative or increase recursion limit)
- Not marking visited before recursing (infinite loop on cycles) — mark when entering, not after
- Forgetting to handle disconnected components — run DFS from each unvisited node
- Confusing pre-order vs post-order processing — matters for topological sort (post-order gives reverse)

## Time/space

- Time: **O(V + E)** — each vertex and edge visited once
- Space: **O(V)** — recursion stack / explicit stack + visited set

## Template

```python
def dfs(graph, node, visited):
    visited.add(node)
    # process node here
    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited)
```