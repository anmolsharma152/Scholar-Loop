---
topic: ml-ai
difficulty: hard
tags: [dl, gnn, graph]
sources:
  - GraphCNN.pdf
---

# Graph Neural Networks (GNNs)

## Graph Representation

- Graphs are irregular data structures representing hierarchical relationships
- **G = (V, E, L)**: V = set of vertices, E = set of edges, L = labels/attributes
- Types: Tree (parent-child hierarchy), DAG (directed acyclic), general graphs with loops/self-loops
- Common in social networks, molecules, knowledge graphs, road networks

## Graph as Matrices

- **Feature matrix X**: Size `N × F₀` — each of N nodes has an F₀-dimensional feature vector
- **Adjacency matrix A**: Size `N × N` — `A[i][j] = 1` if edge exists between nodes i and j
- Self-loops represented on diagonal
- Both X and A are inputs to a GCN

## GCN (Graph Convolutional Network)

- **Core propagation rule**: `H^{(l+1)} = f(H^{(l)}, A)` where H⁰ = X
- Each layer transforms: `H^{(l+1)} = σ(D̃^{-½} Ã D̃^{-½} H^{(l)} W^{(l)})`
  - `Ã = A + I` (adjacency with self-loops)
  - `D̃` = diagonal degree matrix of Ã
  - `W^{(l)}` = learnable weight matrix
- **Dimension change per layer**: `F_l → F_{l+1}` via weight matrix
- After K hidden layers: node features aggregate information from K-hop neighborhood
- Even with few layers, GCN extracts meaningful node feature representations

## Two Types of GNNs

1. **Spectral**: Based on graph signal processing, Laplacian eigenvectors (theoretical foundation)
2. **Spatial**: Direct message passing on graph structure (more practical, scalable)

## Message Passing Framework

- Each node aggregates messages from its neighbors
- Three phases per layer:
  1. **Message computation**: Transform neighbor features `m_j = M(h_j)`
  2. **Aggregation**: Combine messages `ā = AGG({m_j : j ∈ N(i)})`
  3. **Update**: Compute new node embedding `h_i' = U(h_i, ā)`
- Aggregation functions: mean, sum, max, attention-weighted

## Graph Attention (GAT)

- Extends GCN with attention mechanism over neighbors
- **Attention coefficients**: `α_ij = softmax(LeakyReLU(a^T [Wh_i || Wh_j]))`
- Each neighbor contributes a different weight based on relevance
- Multi-head attention for stability
- Better than GCN when neighbor importance varies

## Graph Pooling

- Reduces graph size while preserving important structural information
- **Readout**: Aggregate all node features into graph-level representation
  - `h_G = READOUT({h_i : i ∈ V})` — sum, mean, max, or attention-weighted
- **Hierarchical pooling**: Coarsen graph progressively (DiffPool, TopKPool)
- Enables graph-level tasks (graph classification)

## Key Properties

- **Permutation invariant**: Output doesn't depend on node ordering
- **Local connectivity**: Each node only sees its neighborhood
- **Shared parameters**: Same weight matrices across all nodes (like CNNs share filters)
- **Depth**: Each layer expands receptive field by one hop

## Applications

| Task | Input | Output |
|------|-------|--------|
| Node classification | Graph + features | Label per node |
| Link prediction | Graph + features | Probability of edge |
| Graph classification | Graph + features | Label per graph |
| Molecular property prediction | Molecule graph | Property value |
| Social network analysis | User graph | Community labels |
