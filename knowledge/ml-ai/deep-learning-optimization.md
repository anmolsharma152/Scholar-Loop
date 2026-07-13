---
topic: ml-ai
difficulty: medium
tags: [dl, optimization, training]
sources:
  - DeepLearning101.pdf
  - LossFunction.pdf
  - DeepLearning104.pdf
---

# Deep Learning Optimization

## Gradient Descent Basics

- Goal: `argmin_W L(W)` — find parameters minimizing loss
- Gradient: `∇L(W)` points in direction of steepest ascent
- Update rule: `W ← W - η · ∇L(W)` (step opposite to gradient)
- **Learning rate η**: Controls step size — too large diverges, too small converges slowly

## Batch Variants

| Variant | Data per Update | Pros | Cons |
|---------|----------------|------|------|
| **Batch GD** | Full dataset | Stable gradients | Slow, memory-heavy |
| **Stochastic (SGD)** | Single sample | Fast updates, noisy | High variance |
| **Mini-batch SGD** | B (e.g., 32-512) samples | Best compromise | Need to tune B |

## Momentum

- Accumulates velocity: `v ← β·v + ∇L(W)`; `W ← W - η·v`
- `β` typically 0.9 — exponentially decaying average of past gradients
- **Benefit**: Accelerates in consistent gradient directions, dampens oscillations
- **Physical analogy**: Ball rolling downhill gains speed, overshoots minima less

## Nesterov Accelerated Gradient (NAG)

- "Look ahead" before computing gradient
- `v ← β·v + ∇L(W - η·β·v)`; `W ← W - η·v`
- Computes gradient at predicted future position
- Better convergence than vanilla momentum

## Adaptive Learning Rate Methods

### AdaGrad

- Per-parameter learning rate: `θ_t ← θ_{t-1} - η / √(Σg² + ε) · g_t`
- Adapts: frequent parameters get smaller LR, rare parameters get larger
- **Problem**: Learning rate shrinks monotonically → training stalls

### RMSProp

- Fixes AdaGrad's decay: uses exponential moving average
- `s_t = β·s_{t-1} + (1-β)·g_t²`; `θ ← θ - η/√(s_t + ε) · g_t`
- `β` = 0.99 controls decay window
- Works well for RNNs and non-stationary objectives

### Adam (Adaptive Moment Estimation)

- Combines momentum + RMSProp
- `m_t = β₁·m_{t-1} + (1-β₁)·g_t` (first moment — mean)
- `v_t = β₂·v_{t-1} + (1-β₂)·g_t²` (second moment — uncentered variance)
- Bias correction: `m̂_t = m_t/(1-β₁ᵗ)`, `v̂_t = v_t/(1-β₂ᵗ)`
- `θ ← θ - η · m̂_t / (√v̂_t + ε)`
- Defaults: β₁=0.9, β₂=0.999, ε=1e-8 — good across many problems

### AdamW

- Decouples weight decay from gradient: `W ← W - η·(m̂/(√v̂+ε) + λ·W)`
- Proper L2 regularization (Adam's L2 is incorrectly scaled by adaptive LR)
- Default optimizer for Transformers and most modern architectures

## Learning Rate Scheduling

- **Step decay**: Reduce LR by factor every K epochs
- **Cosine annealing**: `η_t = η_min + ½(η_max - η_min)(1 + cos(πt/T))`
- **Warmup**: Start with small LR, linearly increase for K steps, then decay
- **One cycle policy**: Warmup to max LR, cosine decay to very small
- Warmup critical for Transformers — avoids early instability

## Gradient Clipping

- **By value**: Clip gradient norms exceeding threshold: `g ← g · min(1, threshold/||g||)`
- **By norm**: `||g|| ≤ threshold` (most common)
- Prevents exploding gradients especially in RNNs
- Typical threshold: 1.0

## Second-Order Methods

- **Newton's method**: `W ← W - H⁻¹ · ∇L` where H is Hessian matrix
  - Uses curvature information for better step direction
  - Computationally expensive: O(n²) for Hessian, O(n³) for inverse
- **L-BFGS**: Limited-memory approximation of Hessian (BFGS)
  - Approximates H⁻¹·g using recent gradient history
  - Works well for small datasets, full-batch settings
  - Rarely used in deep learning (mini-batch stochasticity breaks it)

## Loss Landscapes

- High-dimensional non-convex surface with many local minima
- **Saddle points**: More common than local minima in high dimensions
- **Flat minima** generalize better than sharp minima
- SGD noise helps escape sharp minima (implicit regularization)
- Loss landscape visualization: loss along random directions in parameter space

## Practical Guidelines

- **Adam/AdamW**: Default choice, especially for Transformers
- **SGD + Momentum**: Often better final accuracy for CNNs (with proper scheduling)
- **Warmup** for > 100M parameter models
- **Gradient clipping** for RNNs and Transformers
- **Learning rate** is most important hyperparameter to tune
