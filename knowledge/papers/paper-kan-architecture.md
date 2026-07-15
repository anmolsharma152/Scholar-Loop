---
topic: papers
difficulty: hard
tags: [paper, kan, neural-networks, kolmogorov-arnold]
last_sent:
review_count: 0
---

# Kolmogorov-Arnold Networks (KAN): Motivation & Architecture

**Authors:** Ziming Liu, Yixuan Wang, Sachin Vaidya, et al. (MIT)
**Published:** ICLR 2025 (arXiv 2404.19756)

## Problem

Multi-layer perceptrons (MLPs) are the universal building blocks of deep learning but have fundamental limitations:
1. **Fixed activation functions** (ReLU, GeLU) applied at nodes, preventing learning of nonlinear transformations at edges
2. **Poor interpretability:** The distributed representation across neurons makes it hard to understand what a network learned
3. **Catastrophic forgetting:** MLPs struggle to adapt to new data without forgetting old patterns
4. **Spectral bias:** MLPs learn low-frequency functions first, struggling with high-frequency details

## Key Idea

KAN replaces the MLP's learnable weights + fixed activation function at nodes with learnable activation functions on edges.

**MLP vs KAN structure:**
- MLP: σ(Wx + b) — linear transformation + nonlinear activation at nodes
- KAN: Σ_i φ_{i,j}(x_i) — learnable 1D spline functions on edges, summed at nodes

**Core theoretical basis:** The Kolmogorov-Arnold representation theorem states that any multivariate continuous function f: [0,1]^n → ℝ can be represented as a finite composition of univariate functions:

f(x₁,...,x_n) = Σ_{q=1}^{2n+1} Φ_q(Σ_{p=1}^n φ_{q,p}(x_p))

KAN generalizes this to deep networks of arbitrary width by stacking KAN layers.

## Architecture Details

Each edge in KAN has a learnable B-spline activation function with learnable parameters (B-spline coefficients and grid points). The standard setup:
- **Spline order:** k = 3 (cubic B-splines)
- **Grid size:** G = 5 (5 intervals between knots, plus extensions)
- **Width setting:** A [3, 3, 1] KAN has 3 input → 3 hidden → 1 output

**Training:** KANs use LBFGS instead of Adam for more effective spline optimization.
