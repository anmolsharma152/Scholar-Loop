---
topic: ml-ai
title: "Naive Bayes & SVM"
difficulty: medium
tags: [ml, naive-bayes, svm]
sources:
  - "ML_Lec6_Naive_Bayes.pdf"
  - "ML_Lec7_SVM.pdf"
---

# Naive Bayes & Support Vector Machines

## Naive Bayes

### Bayes Classifier (Optimal)
- The theoretically optimal classifier minimizes expected error.
- Estimate `P(y|x)` directly: `P̂(y|x) = P̂(y,x) / P̂(x)`.
- **Problem**: In high dimensions or continuous spaces, `|B|→0` and `|C|→0` — never enough identical training points.

### Naive Bayes Assumption
By Bayes' Rule: `P(y|x) = P(x|y)P(y) / P(x)`

**Key assumption**: features are **conditionally independent** given the label:
```
P(x|y) = ∏_α P(xα|y)
```

### Classifier
```
h(x) = argmax_y  P(y) ∏_α P(xα|y)
```
In log-space:
```
h(x) = argmax_y  [log P(y) + Σ_α log P(xα|y)]
```

### Estimating Parameters

#### Prior P(y = c)
```
P(y = c) = (1/n) Σᵢ I(yᵢ = c) = πc
```

#### Categorical Features
- Feature α takes values in `{f₁, ..., f_{Kα}}`.
- `P(xα = j | y = c) = [θjc]α` with constraint `Σⱼ [θjc]α = 1`.
- Estimate via MLE (counting).

#### Laplace Smoothing
To handle unseen feature values, add α (typically 1) to counts:
```
P(xα = j | y = c) = (count(xα=j, y=c) + α) / (count(y=c) + α·Kα)
```
This prevents zero probabilities.

### Strengths & Weaknesses
- **Strengths**: fast, works well with small data, good for text classification (spam filtering).
- **Weaknesses**: conditional independence assumption is often violated; correlated features degrade performance.

## Support Vector Machine (SVM)

### Maximum Margin Classifier
Given binary labels {+1, -1}, define linear classifier:
```
h(x) = sign(wᵀx + b)
```

### Why Maximum Margin?
- If data is linearly separable, **infinitely many** separating hyperplanes exist.
- The best is the one that **maximizes distance to the closest point** from both classes.

### Margin Formulation
Distance from point x to hyperplane H: `|wᵀx + b| / ||w||`

Margin: `γ(w,b) = min_{x∈D} |wᵀx + b| / ||w||`

### Optimization Problem
Due to scale invariability, fix `min |wᵀx + b| = 1`, then maximize `1/||w||`:

```
min  (1/2)||w||²
s.t. yᵢ(wᵀxᵢ + b) ≥ 1  ∀i
```
This is a **convex quadratic program** — guaranteed global optimum.

### Support Vectors
Points where `yᵢ(wᵀxᵢ + b) = 1` lie exactly on the margin boundaries. Only these points determine the hyperplane.

### Kernel Trick
When data is not linearly separable in original space, map to higher-dimensional feature space via `φ(x)`:
```
K(x, x') = φ(x)ᵀφ(x')
```
Compute inner products in high-dimensional space **without explicitly computing φ(x)**.

**Common Kernels**:
- **Linear**: `K(x,x') = xᵀx'`
- **Polynomial**: `K(x,x') = (xᵀx' + c)^d`
- **RBF (Gaussian)**: `K(x,x') = exp(-γ||x-x'||²)` — maps to infinite-dimensional space.

### Soft-Margin SVM
When data is not perfectly separable, introduce slack variables ξᵢ:
```
min  (1/2)||w||² + C Σ ξᵢ
s.t. yᵢ(wᵀxᵢ + b) ≥ 1 - ξᵢ
     ξᵢ ≥ 0
```
- **C** controls the tradeoff: large C → less misclassification, small C → wider margin.

## Key Takeaways
- **Naive Bayes**: Simple probabilistic classifier; strong independence assumption; works surprisingly well in practice.
- **SVM**: Geometric approach via maximum margin; kernel trick enables nonlinear boundaries; soft-margin handles noise.
