---
topic: ml-ai
title: "Bias-Variance Tradeoff, Decision Trees & Ensembles"
difficulty: hard
tags: [ml, trees, ensemble]
sources:
  - "ML_Lec8_Bias_Variance_Tradeoff.pdf"
  - "ML_Lec9_Decision_Tree.pdf"
  - "ML_Lec10_Bagging.pdf"
  - "ML_Lec11_Boosting.pdf"
---

# Bias-Variance Tradeoff, Decision Trees & Ensembles

## Bias-Variance Decomposition

### Setup
Dataset D drawn i.i.d. from P(X,Y). Algorithm A learns h_D = A(D).
Expected label: `ȳ(x) = E_{y|x}[Y]`
Expected classifier: `h̄ = E_D[h_D]`

### Decomposition (Squared Loss)
```
E[(h_D(x) - y)²] = Bias² + Variance + Noise
```
where:
- **Bias²** = `E_x[(h̄(x) - ȳ(x))²]` — systematic error of the algorithm
- **Variance** = `E_{x,D}[(h_D(x) - h̄(x))²]` — sensitivity to training data
- **Noise** = `E_{x,y}[(ȳ(x) - y)²]` — irreducible error

### Key Insight
- **High bias** → underfitting (model too simple).
- **High variance** → overfitting (model too sensitive to training data).
- Total error = Bias² + Variance + Noise. Reducing one may increase the other.

## Decision Trees

### Structure
- **Internal nodes**: test on an attribute.
- **Branches**: value of that attribute.
- **Leaf nodes**: predict class (or probability P(Y|X ∈ leaf)).
- Represents a **disjunction of conjunctions** of attribute tests.

### ID3 Algorithm (Quinlan)
Greedy top-down construction:
1. At each node, pick the attribute that **best separates** examples.
2. Split on that attribute.
3. Repeat recursively until stopping condition.

### Information Gain (Entropy-Based Splitting)
**Entropy**: `H(X) = -Σ P(X=i) log₂ P(X=i)`
- H = 0: all same class (pure).
- H = 1: equal split (max impurity).

**Conditional Entropy**: `H(X|Y) = Σᵧ P(Y=v) H(X|Y=v)`

**Information Gain**: `IG(Y,A) = H(Y) - H(Y|A)`
- Select attribute with highest IG.

### Gini Impurity (CART)
```
Gini(S) = 1 - Σᵢ pᵢ²
```
- Gini = 0: pure node.
- CART uses Gini for splitting; supports both classification and regression.

### Pruning
- **Pre-pruning**: stop growing tree early (max depth, min samples).
- **Post-pruning**: grow full tree, then remove branches that don't improve validation performance.
- Pruning reduces overfitting (variance).

## Bagging (Bootstrap Aggregating)

### Motivation
From bias-variance decomposition, we want to **reduce variance**: `E[(h_D(x) - h̄(x))²] → 0`.

### Weak Law of Large Numbers
```
(1/m) Σ h_{Dᵢ} → h̄  as m → ∞
```
Averaging many classifiers reduces variance.

### Algorithm
1. Sample m datasets D₁,...,Dₘ from D **with replacement** (bootstrap).
2. Train classifier hⱼ on each Dⱼ.
3. Final classifier: `h(x) = (1/m) Σ hⱼ(x)`

### Out-of-Bag (OOB) Error
- Each (xᵢ, yᵢ) is absent from some bootstrap samples.
- Average predictions of classifiers that didn't see (xᵢ, yᵢ) → acts as test error estimate.

### Random Forest
Bagged decision trees with an extra twist:
- At each split, randomly subsample **k ≤ d features** (without replacement) and only consider those.
- This **decorrelates** trees, further reducing variance.

## Boosting

### Core Idea
Combine many **weak learners** (error ≤ 1/2 - γ) into a **strong learner** (error ≤ ε).

### AdaBoost Algorithm
1. Initialize uniform weights: D₁(i) = 1/m.
2. For t = 1 to T:
   - Train weak classifier hₜ on weighted data Dₜ.
   - Compute error: εₜ = P_{x~Dₜ}(hₜ(xᵢ) ≠ yᵢ).
   - Compute classifier weight: `αₜ = (1/2) ln((1-εₜ)/εₜ)`.
   - Update weights:
     ```
     D_{t+1}(i) ∝ Dₜ(i) · exp(-αₜ yᵢ hₜ(xᵢ))
     ```
   - (Misclassified examples get higher weight; correct ones get lower.)
3. Final: `H(x) = sign(Σₜ αₜ hₜ(x))`

### Gradient Boosting
- Sequentially fits new trees to **residual errors** of the ensemble.
- Each new tree corrects the mistakes of the previous ones.
- Uses gradient descent in function space.

### XGBoost
- Scalable, regularized gradient boosting.
- Adds L1/L2 regularization to tree weights.
- Approximate split finding for speed.
- Handles missing values natively.

## Key Takeaways
- **Bias-variance tradeoff**: central tension in model selection.
- **Decision trees**: intuitive, interpretable, prone to overfitting.
- **Bagging/Random Forest**: reduce variance via averaging; parallelizable.
- **Boosting**: reduce bias by sequentially focusing on hard examples.
