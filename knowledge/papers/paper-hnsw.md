---
topic: papers
difficulty: hard
last_sent:
review_count: 0
tags:
  - paper
  - nearest-neighbor-search
  - graphs
  - approximate-nn
  - data-structures
---

# Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs

**Authors:** Yu. A. Malkov, D. A. Yashunin (Institute of Applied Physics, Russian Academy of Sciences)
**Published:** IEEE Transactions on Pattern Analysis and Machine Intelligence (2020)
**arXiv:** N/A

## Problem & Motivation

Exact K-nearest neighbor search (K-NNS) scales linearly with dataset size, making it infeasible for large-scale applications like image retrieval, semantic search, and non-parametric ML. Existing approximate nearest neighbor search (ANNS) methods based on locality-sensitive hashing (LSH) or product quantization (PQ) had limitations. Proximity graph algorithms offered better performance on high-dimensional data but suffered from power-law scaling of routing (number of hops grows as a power of dataset size), causing severe degradation on low-dimensional or clustered data. The challenge was to achieve logarithmic complexity scaling while being fully graph-based without auxiliary structures.

## Key Idea / Architecture

HNSW builds a multi-layer hierarchical structure of proximity graphs, analogous to a skip list generalized to metric spaces. Each element is assigned a maximum layer l drawn from an exponentially decaying probability distribution: P(l) ∝ e^{-mL · l}, where mL = 1/ln(M) is the normalization factor and M is the number of connections per element. This ensures logarithmic scaling of the number of layers.

**Layer structure:** Upper layers contain only a small fraction of elements with long-range links, while lower layers contain all elements with short-range links approximating the Delaunay graph. This separates links by characteristic distance scales.

**Search algorithm:** Starting from a fixed entry point at the top layer, the algorithm performs greedy routing within each layer until reaching a local minimum, then descends to the next lower layer, restarting from that local minimum. On the top layers (ef=1), only the single closest neighbor is followed. On lower layers (ef > 1), a dynamic list W of ef closest found elements is maintained using two priority queues.

**Insertion algorithm:** A new element q is assigned level l. From the top layer down to l+1, greedy search finds the nearest entry point. From min(L, l) down to 0, efConstruction nearest neighbors are found, and M connections are selected using either simple nearest selection or a heuristic that accounts for inter-candidate distances to create diverse connections. If a node exceeds Mmax connections, its connection list is shrunk using the same selection algorithm.

**Neighbor selection heuristic:** Candidates are examined from nearest to farest. A connection is created only if the candidate is closer to the base element than any already-connected candidate. This produces near-exact relative neighborhood graph subgraphs, maintaining global connectivity even for highly clustered data where simple nearest-neighbor selection fails.

**Complexity:** Under the assumption of exact Delaunay graphs, the expected number of steps per layer is bounded by 1/(1-e^{-mL}), independent of dataset size. With O(log(N)) layers, total search complexity is O(log(N)). Empirically, for d=4 random vectors, the ef parameter required to reach fixed recall saturates with increasing dataset size.

## Key Contributions

1. Multi-layer hierarchical graph structure separating links by distance scale, enabling logarithmic search complexity.
2. Heuristic neighbor selection maintaining global graph connectivity for clustered data, where naive approaches fail catastrophically.
3. Fully graph-based structure with no auxiliary data structures, unlike hybrid approaches combining trees/quantization with graphs.
4. Construction parallelizable with few synchronization points and no measurable quality degradation.

## Results (Specific Numbers)

- 1M SIFT (d=128): HNSW achieves recall 0.9 at ~1ms query time, strongly outperforming NSW, Annoy, VP-tree, FLANN
- 30M random vectors (d=4): HNSW at recall 0.999 in ~0.15ms, orders of magnitude faster than NSW
- 2M CoPhIR (d=272): HNSW clearly outperforms all competitors at all recall levels
- 4M Wiki-sparse (d=105, sparse cosine): HNSW leads over NSW and NAPP
- 5M SIFT construction: ~42 minutes on 4×10-core Xeon with efConstruction=40; ~5.6 hours with efConstruction=500
- Memory: 60–450 bytes per object depending on M (range 6–48)
- On low-dimensional data (wiki-8, JS-divergine), HNSW improves over NSW by nearly 3 orders of magnitude
- SIFT-1M recall@1: HNSW 0.997 vs. NSW 0.982 vs. Annoy 0.968 (ef=128, M=16)
- SIFT-1M query throughput: HNSW 8,200 QPS vs. NSW 1,200 QPS vs. Annoy 3,400 QPS (recall 0.95)
- 100M SIFT scaling: HNSW query time grows O(log N); NSW grows as O(N^0.37)
- Construction quality tradeoff: efConstruction=40 → recall 0.95; efConstruction=500 → recall 0.998
- 1B random vectors (d=128): HNSW query time ~5ms at recall 0.99, 10× faster than hierarchical NSW variants
- NSW baseline: recall 0.999 requires ~15ms at 30M vectors; HNSW requires ~0.15ms (100× improvement)

## Why It Matters / Impact

HNSW became the dominant approximate nearest neighbor search algorithm, adopted in production systems including Elasticsearch, Milvus, Weaviate, Qdrant, and Facebook's FAISS library. It provides the best trade-off between search speed, recall, and memory for most practical use cases. The algorithm's ability to work in general metric spaces (not just vector spaces) broadened its applicability to text similarity, genomics, and other domains.

## Weaknesses / Limitations

1. Memory consumption is proportional to M (60–450 bytes/object overhead) since it stores explicit graph connections, unlike product quantization methods that compress vectors.
2. For extremely high-dimensional data (d > 1000), the advantage over LSH-based methods diminishes.
3. Incremental construction is inherently sequential (new elements connect to existing structure), making fully parallel construction challenging.
4. The analysis of logarithmic complexity relies on assumptions about Delaunay graph approximation that may not hold in exotic metric spaces.
5. Parameter selection (M, mL, efConstruction, Mmax0) requires tuning and does not have universal optimal values across all datasets.

## Follow-up Work

- HNSWlib: Optimized C++/Python implementation with memory-efficient header-only version.
- ONNG (Navigating-ey-Near-Graph): Combines HNSW with product quantization for billion-scale search.
- CAGRA: GPU-accelerated concurrent ANNS graph construction.
- HNSW integration into FAISS, becoming the default graph-based index.
- Weaviate integration: HNSW as primary indexing backend with quantization support.
- Qdrant: Rust-based vector database using HNSW with on-disk graph compression.
