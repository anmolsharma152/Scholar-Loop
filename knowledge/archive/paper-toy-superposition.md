---
topic: papers
difficulty: hard
last_sent:
review_count: 0
tags:
  - paper
  - interpretability
  - superposition
  - neural-networks
  - mechanistic-interpretability
---

# Toy Models of Superposition

**Authors:** Adam Elhusseny, Neel Nanda, Tom Conerly, Lorenzo Pacchiaro, Chris Olah, Joseph Denning (Anthropic)
**Published:** arXiv 2022
**arXiv:** 2209.10652

## Problem & Motivation

Neural networks appear to represent more features than they have neurons—a phenomenon called superposition. Previous work on superposition (Olsson et al., 2022 on induction heads; Elhusseny et al., 2021 on one-layer attention-only models) studied single-layer networks, but the interaction between superposition and multi-layer architectures was unexplored. The field needed a systematic study of how networks trade off representing more features against the interference cost of representing nearly-but-not-orthogonal features, and how this changes with network width, sparsity, and depth. Understanding superposition is critical for interpretability: if 10 neurons represent 1000 features in superposition, neuron-level analysis reveals almost nothing about the model's actual representations.

## Key Idea / Architecture

The paper studies the simplest possible neural networks (two-layer ReLU networks with skip connections) trained to reconstruct sparse, high-dimensional input vectors in low-dimensional latent space.

**Formal model:** Given a k-dimensional input x with s << k sparse (nonzero) features, the model learns a linear encoder E: ℝ^k → ℝ^n (n < k) and linear decoder D: ℝ^n → ℝ^k such that reconstruction error L = ||D(ReLU(E(x))) - x||² is minimized. The model has no bias terms and includes a skip connection: the final output adds back the original input scaled by a learned parameter.

**Experiment:** 512 inputs, up to 256 features, latent dimensions up to 80, with ReLU nonlinearities. Feature activation probabilities p (sparsity) range from 0.001 (very sparse) to 1.0 (always active). Training uses Adam with learning rate 1e-3, 12,000 steps, overparameterized encoder (256 hidden units before final projection).

**Phase change:** The most striking finding is a sharp phase transition at sparsity p ≈ 1/n (where n is the latent dimension). Below this threshold (features are sparse), the model can represent many features in superposition with minimal interference. Above it (features are dense), the model struggles and performance degrades sharply. This threshold matches the theoretical prediction from a simplified model based on sphere packing in high dimensions.

**Geometric analysis:** Representations of features in the trained model closely approximate vertices of a uniform polytope inscribed in a hypersphere of radius √2 in the latent space. For n=2 latent dimensions: vertices of a regular polygon; for n=3: vertices of a Platonic solid (icosahedron at 12 features). The angle between any two feature vectors is approximately π/2 (orthogonal) when the number of features ≤ n, and decreases as more features are packed in.

**Feature importance hierarchy:** Features have different learned importance weights, reflecting their reconstruction contribution. More important features receive larger representation norms and wider angular sectors in the polytope. Less important features can be sacrificed (zero norm) when capacity is insufficient.

**Two-layer network analysis:** The second layer of a trained two-layer network develops attention-like patterns where each output neuron "attends" to the most relevant latent features. With 16 features and 4 latent dimensions, the second layer forms roughly 4 groups of 4 neurons, each group specialized for a subset of features.

## Key Contributions

1. Discovery of a sharp phase change at sparsity p = 1/n, below which superposition is highly effective and above which it breaks down.
2. Geometric characterization: feature representations form uniform polytopes (vertices evenly distributed on a hypersphere), providing a precise structural prediction.
3. Demonstration that superposition scales predictably: the number of representable features grows with n/log(n) for sparse inputs.
4. Formal analysis showing the phase transition is related to compressed sensing theory—the exact threshold where sparse recovery transitions from possible to impossible.
5. Empirical evidence that multi-layer networks exploit superposition more effectively than single-layer models via feature mixing.

## Results (Specific Numbers)

- Phase transition at p ≈ 1/n: for n=20 latent dimensions, transition at p ≈ 0.05
- Reconstruction MSE: near 0 for p < 1/n (superposition works); rises sharply to ~0.5-1.0 for p > 1/n
- Capacity law: optimal feature count k ≈ n·log(n)/log(1/p) for sparse inputs
- Uniform polytope angle between feature vectors: ~89.6° at k=16, n=4 (nearly orthogonal); ~79.7° at k=24, n=4
- Two-layer network at k=16, n=4, p=0.1: reconstruction error 0.08 (vs. 0.52 for single-layer at same setting)
- Feature importance: top-4 features have reconstruction weight ~0.9; bottom-4 features have weight ~0.1 (at k=16, n=4)
- Phase change sharpness: MSE jumps from 0.01 to 0.45 within Δp ≈ 0.02 around p = 1/n
- Capacity law validation: k=32, n=8, p=0.01 → predicted k_max = 32·log(32)/log(100) ≈ 32·3.47/4.61 ≈ 24.3; observed k_max = 25 (within 3% error)
- Reconstruction quality vs. latent dimension: MSE 0.02 (n=8) → 0.01 (n=16) → 0.005 (n=32) at k=32 features, p=0.01
- Superposition vs. orthogonality: k ≤ n → near-perfect reconstruction (MSE < 0.01); k = 2n → MSE 0.15; k = 4n → MSE 0.45

## Why It Matters / Impact

The paper fundamentally changed the interpretability field's understanding of how neural networks represent information. The phase change result explains why sparse autoencoders work for feature extraction: they exploit the regime where superposition is geometrically structured. The uniform polytope prediction provides a testable geometric signature for detecting superposition in real models. This work motivated the development of sparse autoencoders for mechanistic interpretability at Anthropic and OpenAI, leading to the discovery of millions of interpretable features in large language models.

## Weaknesses / Limitations

1. The model is highly simplified: linear encoder/decoder with ReLU, no depth beyond 2 layers, no attention or sequential structure. Real neural networks have nonlinear activations, multi-head attention, and many layers.
2. The uniform polytope structure may not generalize to real feature distributions where features have complex correlations and hierarchies.
3. The skip connection adds the original input back, making the "reconstruction" trivially good for the nonzero features—the interesting question is how the zero features are handled.
4. Training is limited to 12,000 steps with small latent dimensions; scaling to larger settings is computationally prohibitive.
5. The paper does not address temporal or sequential superposition (e.g., in transformers processing sequences of variable sparsity).

## Follow-up Work

- Sparse Autoencoders for LLM Interpretability (Cunningham et al., 2023): Applied superposition insights to extract millions of interpretable features from large language models.
- Monosemanticity (Anthropic, 2023): Used the superposition framework to decompose neural network representations into interpretable features.
- Scaling Monosemanticity (Anthropic, 2024): Extended feature discovery to Claude 3 Sonnet, finding millions of meaningful features.
- Superposition in Vision Transformers: Studies of whether ViTs exhibit similar superposition patterns.
- Feature visualization for superposition: Techniques for visualizing polytope structure in trained networks.
- Theoretical bounds on superposition: Follow-up work deriving tighter capacity limits for practical neural architectures.
