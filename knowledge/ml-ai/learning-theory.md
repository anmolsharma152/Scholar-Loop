---
topic: ml-ai
title: "Learning Theory"
difficulty: hard
tags: [ml, learning-theory]
sources:
  - "ML_Lec_14_Learning_Theory.pdf"
---

# Learning Theory

## Goal of Learning Theory
- Understand what kinds of tasks are **learnable**.
- What kind of **data** is required?
- What are the **space/time requirements** of learning algorithms?
- Develop algorithms with **provable guarantees**.

## Prototypical Concept Learning Task

### Given
- Instances X (e.g., ℝᵈ or {0,1}ᵈ)
- Distribution D over X
- Target concept c
- Hypothesis space H
- Training examples S = {(xᵢ, c(xᵢ))}, xᵢ i.i.d. from D

### Determine
- Find h ∈ H such that h(x) = c(x) for all x in S (consistency).
- Find h ∈ H such that h(x) = c(x) for all x in X (generalization).

## Error of a Hypothesis

### True Error
```
error_D(h) = Pr_{x~D}[c(x) ≠ h(x)]
```
Probability h misclassifies a random instance from D.

### Approximately Correct
A hypothesis h is **approximately correct** if `error_D(h) ≤ ε`.

## PAC Learning (Probably Approximately Correct)

### Definition
A concept class C is **PAC-learnable** if there exists an algorithm A that, for any:
- ε > 0 (error parameter)
- δ > 0 (confidence parameter)

outputs h ∈ H such that with probability ≥ (1-δ):
```
error_D(h) ≤ ε
```
in time polynomial in `1/ε`, `1/δ`, `n` (instance length), and `size(c)`.

### Parameters
- **ε** (error): tolerance for misclassification.
- **δ** (confidence): probability of failing to find good h.
- **n**: number of features (instance length).
- **size(c)**: complexity of target concept.

## Sample Complexity

### Consistent Learner Theorem
```
m ≥ (1/ε) [ln(|H|) + ln(1/δ)]
```
labeled examples suffice so that with probability ≥ (1-δ), all h ∈ H with `error_D(h) ≥ ε` have `error_S(h) > 0`.

**Interpretation**:
- **Inversely linear** in ε (tighter error → more data needed).
- **Logarithmic** in |H| (larger hypothesis spaces need slightly more data, not dramatically more).
- **Logarithmic** in 1/δ (higher confidence → slightly more data).

### Proof Sketch
- Consider "bad" hypotheses H_bad = {h : error_D(h) ≥ ε}.
- For a single bad h: Pr[h consistent with m examples] ≤ (1-ε)ᵐ.
- By union bound: Pr[∃ h ∈ H_bad consistent] ≤ |H|(1-ε)ᵐ.
- Set ≤ δ and solve for m.

## VC Dimension

### Motivation
The |H| in sample complexity can be infinite for continuous hypothesis spaces (e.g., halfspaces in ℝᵈ).

### Shattering
A hypothesis class H **shatters** a set of points S if H can realize every possible labeling of S.

### VC Dimension
```
VC(H) = max |S| such that H shatters S
```

### VC-Based Sample Complexity
```
m ≥ (1/ε) [VC(H) · ln(1/ε) + ln(1/δ)]
```
Replaces |H| with VC(H), which is finite even for infinite hypothesis spaces.

## Empirical Risk Minimization (ERM)

### Principle
Choose h that minimizes **training error**:
```
ĥ = argmin_{h∈H} error_S(h)
```

### Connection to PAC
If m is large enough (per sample complexity bounds), ERM guarantees small true error with high probability.

## Regularization

### Motivation
Control model complexity to prevent overfitting (reduce variance at cost of slight bias increase).

### L1 Regularization (Lasso)
```
J(θ) = Loss + λ Σ |θⱼ|
```
- Encourages **sparsity** (many weights become exactly 0).
- Feature selection effect.

### L2 Regularization (Ridge)
```
J(θ) = Loss + λ Σ θⱼ²
```
- Encourages **small weights** but rarely zero.
- Prevents any single feature from dominating.

### ElasticNet
```
J(θ) = Loss + λ₁ Σ |θⱼ| + λ₂ Σ θⱼ²
```
- Combines L1 and L2.
- Best of both worlds: sparsity + stability.

### Regularization & Bias-Variance
- Increasing λ → higher bias, lower variance.
- Decreasing λ → lower bias, higher variance.
- Optimal λ balances the tradeoff.

## Key Takeaways
- **PAC learning**: formalizes "probably approximately correct" generalization.
- **Sample complexity** scales linearly with 1/ε, logarithmically with hypothesis space size.
- **VC dimension** measures capacity of hypothesis class; replaces |H| in bounds.
- **Regularization** controls complexity: L1 for sparsity, L2 for small weights, ElasticNet for both.
