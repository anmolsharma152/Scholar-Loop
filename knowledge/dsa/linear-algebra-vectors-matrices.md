---
difficulty: medium
last_sent: 2026-07-14 04:31:55.754501+00:00
review_count: 1
sequence: 1
tags:
- math
- linear-algebra
topic: dsa
---

# Linear Algebra: Vectors, Matrices & Systems of Equations

Source: Masai_X_IITMandi Trimester 1 — Dr. Indu Joshi, IIT Mandi

---

## 1. Vectors

A vector is an ordered tuple v = [v1, v2, ..., vn] in R^n. Geometrically it encodes direction and magnitude.

### Vector Operations
- **Addition**: u + v = [u1+v1, u2+v2, ..., un+vn]
- **Subtraction**: u - v = [u1-v1, u2-v2, ..., un-vn]
- **Dot Product**: u · v = u1v1 + u2v2 + ... + unvn
- **Magnitude**: |v| = sqrt(v · v) = sqrt(v1^2 + v2^2 + ... + vn^2)
- **Angle**: cos(theta) = (u · v) / (|u| |v|)

### Linear Combination
Given set S = {v1, v2, ..., vk}, a vector v = a1*v1 + a2*v2 + ... + ak*vk is a **linear combination** where a_i are scalars.

### Linear Independence
Set S = {v1, ..., vn} is **linearly independent** if a1*v1 + ... + an*vn = 0 implies all a_i = 0. Otherwise **linearly dependent**.

Key facts:
- In R^n, any set of more than n vectors is linearly dependent
- Any set containing the zero vector is linearly dependent
- A set of orthogonal vectors is always linearly independent

### Orthogonal & Orthonormal
- **Orthogonal**: vi · vj = 0 for all i != j
- **Orthonormal**: orthogonal + each vector has unit length (|vi| = 1)

---

## 2. Matrices

A matrix A is an m x n array of scalars a_ij where i = rows, j = columns.

### Special Matrices
- **Diagonal**: all off-diagonal entries are zero
- **Upper Triangular**: all entries below main diagonal are zero
- **Lower Triangular**: all entries above main diagonal are zero
- **Identity (I)**: diagonal matrix with all 1s on diagonal
- **Symmetric**: A = A^T

### Matrix Operations
- **Addition/Subtraction**: element-wise, matrices must be same size
- **Scalar Multiplication**: multiply every element by scalar gamma
- **Multiplication**: (X * Y)_ij = sum_k (x_ik * y_kj). Columns of X must equal rows of Y.
  - X_(m x n) * Y_(n x p) = Z_(m x p)
  - Matrix multiplication is NOT commutative: XY != YX in general

---

## 3. Echelon Form & Rank

### Elementary Row Operations
1. Multiply a row by non-zero scalar: Rj -> c*Rj
2. Replace row r by row r + c * row s: Rr -> Rr + c*Rs
3. Interchange two rows: Ri <-> Rj

Two matrices are **row equivalent** if one can be obtained from the other by finite row operations.

### Echelon Form
A matrix is in echelon form if:
1. All zero rows are at the bottom
2. Each leading nonzero entry is to the right of the leading nonzero entry in the row above

### Rank
**rank(A)** = number of non-zero rows in echelon form = max number of linearly independent rows (or columns).

Properties:
- rank(A) <= min(m, n) for A in R^(m x n)
- rank(A) = rank(A^T)
- rank(cA) = rank(A) for c != 0
- rank(A) = n iff det(A) != 0 (square matrix)
- Elementary row/column operations are rank-preserving

---

## 4. Systems of Linear Equations

Standard form: **Ax = b** where A is coefficient matrix, x is unknown vector, b is constant vector.

### Types
- **Homogeneous**: b = 0 (always consistent, has trivial solution x = 0)
- **Non-homogeneous**: b != 0
- **Consistent**: at least one solution exists
- **Inconsistent**: no solution

### Augmented Matrix [A|b]
Order is m x (n+1). Always rank([A|b]) >= rank(A).

### Solution Criteria

**Homogeneous (Ax = 0)**:
- rank(A) = n (unknowns) -> unique trivial solution x = 0
- rank(A) < n -> infinitely many non-trivial solutions

**Non-homogeneous (Ax = b)**:
- rank([A|b]) != rank(A) -> inconsistent (no solution)
- rank([A|b]) = rank(A) = r:
  - r = n -> unique solution
  - r < n -> infinitely many solutions (assign n-r free variables)

---

## 5. Vector Spaces & Subspaces

### Field
A set F with addition and multiplication satisfying closure, commutativity, associativity, identity, inverse, and distributivity. Examples: R, C, Q.

### Vector Space
V(F) is a vector space over field F if:
- Closed under addition and scalar multiplication
- Contains zero vector
- Every vector has an additive inverse
- Satisfies associativity, commutativity, distributivity of operations

### Subspace
A subset W of vector space V is a subspace if W itself forms a vector space under the same operations. Must contain zero vector and be closed under addition and scalar multiplication.

---

## 6. Basis & Dimension

### Basis
A basis for V is a set of linearly independent vectors that spans V. Every vector in V can be uniquely written as a linear combination of basis vectors.

Standard basis for R^n: e1 = [1,0,...,0], e2 = [0,1,...,0], ..., en = [0,0,...,1]

### Dimension
**dim(V)** = number of vectors in any basis of V. A finite-dimensional vector space has a finite basis.

- dim(R^n) = n
- dim(R^(m x n)) = m*n
- dim(R^(2x2 symmetric)) = 3

---

## Key Connections to ML

| Concept | ML Application |
|---------|---------------|
| Dot product | Similarity measurement, projections |
| Rank | Dimensionality reduction (PCA) |
| Echelon form | Solving linear regression |
| Basis | Feature space representation |
| Linear independence | Feature selection |
| Orthogonal vectors | Noise reduction, decorrelation |