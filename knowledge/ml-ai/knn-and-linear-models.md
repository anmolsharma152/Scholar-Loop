---
topic: ml-ai
title: "KNN & Linear Models"
difficulty: medium
tags: [ml, knn, regression]
sources:
  - "ML_Lec3_KNN_curse_of_dimensionality.pdf"
  - "ML_Lec4_Linear_Regression.pdf"
  - "ML_Lec5_Logistic_Regression.pdf"
---

# KNN & Linear Models

## K-Nearest Neighbors (KNN)

### Core Idea
- **Assumption**: similar inputs have similar outputs.
- **Rule**: For test input x, assign the most common label among its k nearest training neighbors.

### Formal Definition
Given test point x, let Sₓ be its k nearest neighbors:
- `Sₓ ⊆ D` with `|Sₓ| = k`
- Every point in D\Sₓ is at least as far from x as the furthest point in Sₓ.
- `h(x) = mode({y″ : (x″, y″) ∈ Sₓ})`

### Distance Metric
Most common: **Minkowski distance**
```
dist(x, z) = (Σᵣ |xᵣ - zᵣ|^p)^(1/p)
```
- p=1: Manhattan, p=2: Euclidean.

### Curse of Dimensionality
- In high-dimensional spaces, points drawn from a distribution **tend to never be close together**.
- Consider unit cube [0,1]ᵈ with k=10 nearest neighbors. Edge length of enclosing hypercube:
  - d=2: ℓ ≈ 0.63
  - d=100: ℓ ≈ 0.955
  - d=1000: ℓ ≈ 0.9954
- As d grows, ℓ → 1: nearest neighbors span **almost the entire space**.
- **All points become nearly equidistant** — "nearest" loses meaning.
- **Practical implication**: kNN degrades badly in high dimensions without dimensionality reduction.

## Linear Regression

### Hypothesis
```
hθ(x) = θ₀ + θ₁x₁ + θ₂x₂ + ... + θₙxₙ = θᵀx
```
(with x₀ = 1 for intercept)

### Cost Function
```
J(θ) = (1/2m) Σᵢ (hθ(x⁽ⁱ⁾) - y⁽ⁱ⁾)²
```

### Gradient Descent
```
θⱼ := θⱼ - α · ∂J(θ)/∂θⱼ
```
- α = learning rate; update all θⱼ simultaneously.
- For linear regression, J(θ) is convex → guaranteed to converge.

### Closed-Form Solution (Normal Equation)
```
θ = (XᵀX)⁻¹Xᵀy
```
- No need for feature scaling.
- Slow when n is very large (inverting XᵀX is O(n³)).

## Logistic Regression

### Motivation
Linear regression outputs are unbounded; for binary classification (y ∈ {0,1}), we need outputs between 0 and 1.

### Sigmoid Function
```
hθ(x) = σ(θᵀx) = 1 / (1 + e^{-θᵀx})
```
- σ(z) → 1 as z → ∞; σ(z) → 0 as z → -∞.
- Output interpreted as **P(y=1 | x; θ)**.

### Derivative of Sigmoid
```
σ'(z) = σ(z)(1 - σ(z))
```
This elegant property simplifies gradient computation.

### Decision Boundary
P(y=1|x) = 0.5 ⟹ θ₀ + Σθⱼxⱼ = 0 — a **linear** boundary in input space.

### Cost Function (Cross-Entropy Loss)
```
J(θ) = -1/m Σ [y⁽ⁱ⁾ log hθ(x⁽ⁱ⁾) + (1-y⁽ⁱ⁾) log(1-hθ(x⁽ⁱ⁾))]
```

### MLE Derivation
```
p(y|x;θ) = (hθ(x))ʸ (1 - hθ(x))^{1-y}
L(θ) = ∏ᵢ (hθ(x⁽ⁱ⁾))^{y⁽ⁱ⁾} (1 - hθ(x⁽ⁱ⁾))^{1-y⁽ⁱ⁾}
```
Minimizing negative log-likelihood gives the cross-entropy loss.

## Key Takeaways
- **KNN**: Simple, non-parametric, but suffers in high dimensions.
- **Linear Regression**: Best for continuous outputs, convex loss, closed-form or GD.
- **Logistic Regression**: Linear classifier via sigmoid + cross-entropy; outputs calibrated probabilities.
