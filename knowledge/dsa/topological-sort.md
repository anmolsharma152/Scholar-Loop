---
difficulty: hard
last_sent: null
review_count: 0
sequence: 16
tags:
- graph
- topological-sort
topic: dsa
---

# Topological sort

A **linear ordering** of vertices in a Directed Acyclic Graph (DAG) such that for every directed edge u → v, u comes before v. Only possible in DAGs. Two main algorithms: **Kahn's algorithm** (BFS, indegree-based) and **DFS with visited states**.

## Kahn's algorithm (BFS)

Count indegrees, push zero-indegree nodes into a queue, process each by removing its outgoing edges.

```python
from collections import deque

def topological_sort_kahn(n, edges):
    graph = [[] for _ in range(n)]
    indegree = [0] * n
    for u, v in edges:
        graph[u].append(v)
        indegree[v] += 1

    q = deque([i for i in range(n) if indegree[i] == 0])
    result = []
    while q:
        u = q.popleft()
        result.append(u)
        for v in graph[u]:
            indegree[v] -= 1
            if indegree[v] == 0:
                q.append(v)

    return result if len(result) == n else []  # empty if cycle
```

## DFS-based approach

Use three states: 0 = unvisited, 1 = visiting, 2 = visited. Detect cycles by encountering a node in state 1.

```python
def topological_sort_dfs(n, edges):
    graph = [[] for _ in range(n)]
    for u, v in edges:
        graph[u].append(v)

    state = [0] * n
    result = []

    def dfs(u):
        if state[u] == 1:
            return False  # cycle
        if state[u] == 2:
            return True
        state[u] = 1
        for v in graph[u]:
            if not dfs(v):
                return False
        state[u] = 2
        result.append(u)  # post-order
        return True

    for i in range(n):
        if not dfs(i):
            return []  # cycle
    return result[::-1]  # reverse post-order
```

## Classic problems

| Problem | Approach |
|---------|----------|
| Course schedule I | Kahn's — can complete if result has all n nodes |
| Course schedule II | Kahn's — return the ordering itself |
| Alien dictionary | Build edges from first differing char; topo sort |
| Minimum height trees | Kahn's from leaves inward (strip leaves iteratively) |
| Longest path in DAG | Topological order + DP relaxation |

## Cycle detection

Both algorithms detect cycles. In Kahn's, a cycle exists when the result size < n (some nodes never reach indegree 0). In DFS, a cycle exists when we encounter a node in the "visiting" state.

## Common bugs

- Forgetting to build reverse adjacency or misdirecting edges
- Not handling multiple edges (indegree counts them correctly)
- Assuming a unique topological order (there can be many)
- Using Kahn's on a graph that might not be a DAG without checking

## Time/space

- Time: **O(V + E)** — each vertex and edge processed once
- Space: **O(V + E)** — adjacency list and indegree/state arrays