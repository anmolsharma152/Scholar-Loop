---
difficulty: medium
last_sent: 2026-07-13 23:24:11.416783+00:00
review_count: 1
sources:
- ML_Lec12_Clustering.pdf
- ML_Lec13_PCA.pdf
tags:
- ml
- clustering
- pca
title: Clustering & PCA
topic: ml-ai
---

# Clustering & Principal Component Analysis

## Clustering

### What is Clustering?
- **Unsupervised learning** technique to group similar data points together.
- Finds hidden structures **without predefined labels**.
- Applications: outlier detection, feature engineering, pattern discovery.

## K-Means Clustering

### Algorithm
1. Choose number of clusters K.
2. Initialize K cluster centroids randomly.
3. **Assignment step**: assign each point to nearest centroid.
4. **Update step**: recompute centroids as mean of assigned points.
5. Repeat 3-4 until convergence (centroids stop moving).

### Objective Function
```
J = Σᵢ₌₁ᴷ Σ_{xⱼ ∈ Cᵢ} ||xⱼ - μᵢ||²
```
Minimizing intra-cluster variance.

### K-Means++
Better initialization: choose centroids that are far apart, reducing sensitivity to initialization.

### Elbow Method
- Plot J (sum of squared distances) vs K.
- The **elbow point** (where marginal improvement drops) suggests the optimal K.

### Strengths & Weaknesses
- **Strengths**: simple, fast, scales well, works for spherical clusters.
- **Weaknesses**: assumes spherical clusters, sensitive to initialization, must specify K, struggles with non-convex shapes and outliers.

## DBSCAN
- Density-based clustering: groups points that are closely packed.
- Can find **arbitrary-shaped clusters**.
- Handles **noise/outliers** naturally.

## Hierarchical Clustering
- **Agglomerative** (bottom-up): merge closest clusters iteratively.
- **Divisive** (top-down): split clusters recursively.
- Produces a **dendrogram** showing merge hierarchy.

## Principal Component Analysis (PCA)

### Motivation
Reduce dimensionality while **preserving maximum variance**.

### Goal
Learn transformation from ℝᵈ → ℝᵏ (k < d):
```
Y = A · X
```
where A is the projection matrix.

### Covariance Matrix
For centered data X:
```
Σ = (1/n) XᵀX
```
- Symmetric matrix capturing pairwise feature correlations.
- Diagonal: variances; Off-diagonal: covariances.

### Eigenvalue Decomposition
The principal components are the **eigenvectors** of the covariance matrix Σ:
```
Σv = λv
```
- **Eigenvector** v: direction that remains unchanged (only scaled).
- **Eigenvalue** λ: amount of variance explained along that direction.

### Computing PCA
1. Center data (subtract mean).
2. Compute covariance matrix Σ.
3. Find eigenvalues and eigenvectors of Σ.
4. Sort eigenvalues in descending order.
5. Select top k eigenvectors → these are the principal components.
6. Project data: `Y = X · Vₖ` where Vₖ contains top k eigenvectors.

### Explained Variance
```
Explained Variance Ratio = λₖ / Σᵢ λᵢ
```
Choose k such that cumulative explained variance ≥ threshold (e.g., 95%).

### Key Properties
- First PC captures **maximum variance**.
- Subsequent PCs capture remaining variance, orthogonal to previous ones.
- PCA is **linear** — for nonlinear structure, consider kernel PCA.

## Key Takeaways
- **K-Means**: fast, simple, but assumes spherical clusters; use elbow method for K.
- **DBSCAN**: handles arbitrary shapes and noise.
- **PCA**: linear dimensionality reduction via eigenvectors of covariance matrix; preserves variance.