---
topic: papers
difficulty: hard
last_sent:
review_count: 0
tags:
  - paper
  - interpretability
  - superposition
---

# Toy Models of Superposition: Phase Change

**Authors:** Adam Elhusseny, Neel Nanda, Tom Conerly, et al. (Anthropic)
**Published:** arXiv 2022 (2209.10652)

## Problem & Motivation

Neural networks appear to represent more features than they have neurons—a phenomenon called superposition. Previous work studied single-layer networks, but the interaction between superposition and multi-layer architectures was unexplored. Understanding superposition is critical for interpretability: if 10 neurons represent 1000 features in superposition, neuron-level analysis reveals almost nothing about the model's actual representations.

## Key Idea

The paper studies the simplest possible neural networks (two-layer ReLU networks with skip connections) trained to reconstruct sparse, high-dimensional input vectors in low-dimensional latent space.

**Formal model:** Given a k-dimensional input x with s << k sparse features, the model learns a linear encoder E: ℝ^k → ℝ^n (n < k) and linear decoder D: ℝ^n → ℝ^k such that reconstruction error L = ||D(ReLU(E(x))) - x||² is minimized.

**Phase change:** The most striking finding is a sharp phase transition at sparsity p ≈ 1/n (where n is the latent dimension). Below this threshold (features are sparse), the model can represent many features in superposition with minimal interference. Above it (features are dense), the model struggles and performance degrades sharply.

**Geometric analysis:** Representations of features closely approximate vertices of a uniform polytope inscribed in a hypersphere of radius √2 in the latent space. For n=2 latent dimensions: vertices of a regular polygon; for n=3: vertices of a Platonic solid (icosahedron at 12 features).

**Feature importance hierarchy:** Features have different learned importance weights. More important features receive larger representation norms and wider angular sectors in the polytope. Less important features can be sacrificed when capacity is insufficient.

## Key Contributions

1. Discovery of a sharp phase change at sparsity p = 1/n, below which superposition is highly effective and above which it breaks down
2. Geometric characterization: feature representations form uniform polytopes
3. Demonstration that superposition scales predictably: the number of representable features grows with n/log(n) for sparse inputs
4. Formal analysis showing the phase transition is related to compressed sensing theory
5. Empirical evidence that multi-layer networks exploit superposition more effectively than single-layer models

## Results

- Phase transition at p ≈ 1/n: for n=20 latent dimensions, transition at p ≈ 0.05
- Reconstruction MSE: near 0 for p < 1/n; rises sharply to ~0.5-1.0 for p > 1/n
- Capacity law: optimal feature count k ≈ n·log(n)/log(1/p) for sparse inputs
- Uniform polytope angle: ~89.6° at k=16, n=4 (nearly orthogonal); ~79.7° at k=24, n=4
- Phase change sharpness: MSE jumps from 0.01 to 0.45 within Δp ≈ 0.02 around p = 1/n
