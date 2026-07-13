---
difficulty: easy
last_sent: null
review_count: 0
tags:
  - graphs
topic: dsa
---

# Graph representation

A graph `G = (V, E)` consists of **vertices** (nodes) and **edges** (connections). Edges can be **directed** (one-way) or **undirected** (two-way). Edges may carry a **weight** (cost, distance).

## Directed vs undirected

| Type | Edge meaning | Example |
|------|-------------|---------|
| Undirected | A-B means A ↔ B | Friend network |
| Directed | A → B means A → B only | Web page links |
| Weighted | Each edge has a numeric cost | Road network |

## Adjacency list (most common)

```python
# undirected, unweighted
graph = {
    0: [1, 2],
    1: [0, 3],
    2: [0],
    3: [1],
}

# weighted: store (neighbor, weight) pairs
graph = {
    0: [(1, 5), (2, 3)],
    1: [(0, 5), (3, 2)],
}
```

Space: **O(V + E)**. Best for sparse graphs.

## Adjacency matrix

```python
# V x V matrix, matrix[u][v] = 1 if edge exists
matrix = [
    [0, 1, 1, 0],
    [1, 0, 0, 1],
    [1, 0, 0, 0],
    [0, 1, 0, 0],
]
```

Space: **O(V²)**. Best for dense graphs or when O(1) edge lookup is critical.

## Edge list

```python
edges = [(0, 1), (0, 2), (1, 3)]
```

Simple, used in Kruskal's algorithm for MST.

## Choosing a representation

| Criterion | Adjacency list | Adjacency matrix |
|-----------|---------------|------------------|
| Space | O(V + E) | O(V²) |
| Edge lookup | O(degree) | O(1) |
| Iterate neighbors | O(degree) | O(V) |
| Add edge | O(1) | O(1) |
| Remove edge | O(degree) | O(1) |

## Common bugs

- Forgetting to add both directions for undirected graphs
- Using 0 vs 1 indexing for vertices
- Confusing edge weight with edge presence in matrices

## Time/space

- Sparse graph (E ≈ V): adjacency list preferred
- Dense graph (E ≈ V²): matrix may be acceptable
- Always consider the graph density when choosing representation
