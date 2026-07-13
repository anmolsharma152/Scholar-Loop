---
difficulty: medium
last_sent:
review_count: 0
tags:
  - math
  - linear-algebra
topic: dsa
---

# Linear Algebra: Eigenvalues, Eigenvectors & Positive Definiteness

Source: Masai_X_IITMandi Trimester 1 — Dr. Indu Joshi, IIT Mandi

---

## 1. Eigenpairs

### Definition
Let A be an n x n matrix. A non-zero vector v is an **eigenvector** of A corresponding to **eigenvalue** lambda (scalar) if:

    A * v = lambda * v

This means applying linear transformation A to v only scales it by factor lambda (no rotation for that vector).

### Computing Eigenpairs

**Step 1**: Form the characteristic equation:

    det(A - lambda * I) = 0

**Step 2**: Solve for lambda (roots of the characteristic polynomial).

**Step 3**: For each lambda, solve (A - lambda*I)v = 0 to find eigenvectors.

### Worked Example
For A = [[2, -2, 3], [1, 1, 1], [1, 3, -1]]:

Characteristic polynomial: -lambda^3 + 2*lambda^2 + 5*lambda - 6 = 0

Roots: lambda = 1, lambda = -2, lambda = 3

For lambda = 3: eigenvector v = [1, 1, 1]^T
For lambda = 1: eigenvector v = [1, -1, -1]^T
For lambda = -2: eigenvector v = [11, 1, -14]^T

---

## 2. Properties of Eigenvalues

1. **Inverse**: If Av = lambda*v, then A^(-1)*v = (1/lambda)*v
   (eigenvalue of inverse is reciprocal)

2. **Powers**: A^k * v = lambda^k * v
   (eigenvalue of A^k is lambda^k)

3. **Determinant**: det(A) = product of all eigenvalues
   det(A) = lambda_1 * lambda_2 * ... * lambda_n

4. **Trace**: tr(A) = sum of all eigenvalues
   tr(A) = lambda_1 + lambda_2 + ... + lambda_n

5. **Characteristic Polynomial**: p_A(lambda) = det(A - lambda*I)
   is degree n polynomial with roots at eigenvalues

6. **Transpose**: A and A^T have the same eigenvalues

7. **Similar Matrices**: Similar matrices have the same eigenvalues

---

## 3. Geometric Interpretation

- Eigenvectors are directions that are invariant under the transformation A
- Eigenvalues tell you how much the eigenvector is stretched/compressed
- lambda > 1: stretching
- 0 < lambda < 1: compression
- lambda < 0: reflection + scaling
- lambda = 0: vector maps to zero (matrix is singular)

---

## 4. Quadratic Forms

For symmetric matrix A in R^(n x n), the **quadratic form** is:

    q(X) = X^T * A * X

### Example
For A = [[1, -1, 2], [-1, 3, 1], [2, 1, 4]] and X = [x1, x2, x3]^T:

    q(X) = x1^2 + 3*x2^2 + 4*x3^2 - 2*x1*x2 + 4*x1*x3 + 2*x2*x3

### Constructing Matrix from Quadratic Form
Given q(X) = x1^2 + 4*x1*x2 + x2^2 + 2*x3^2 + 6*x2*x3:

    A = [[1, 2, 0], [2, 1, 3], [0, 3, 2]]

Diagonal entries = coefficients of squared terms. Off-diagonal a_ij = half coefficient of x_i*x_j term.

---

## 5. Positive Definite & Semi-Definite Matrices

### Positive Semi-Definite (PSD)
Symmetric matrix A is PSD if for all X in R^n:

    q(X) = X^T * A * X >= 0

### Positive Definite (PD)
Symmetric matrix A is PD if for all non-zero X in R^n:

    q(X) = X^T * A * X > 0

### Eigenvalue Characterization (Key Theorem)

**A symmetric matrix is positive (semi-)definite if and only if all its eigenvalues are positive (non-negative).**

Proof sketch: Express X as linear combination of orthonormal eigenvectors:
    X = c1*v1 + c2*v2 + ... + cn*vn

Then: X^T * A * X = sum_i (lambda_i * c_i^2)

- If all lambda_i > 0: sum is > 0 for any non-zero X -> PD
- If all lambda_i >= 0: sum is >= 0 for any X -> PSD

### Example: Check if PD
A = [[2, -1, 0], [-1, 2, -1], [0, -1, 2]]

Characteristic polynomial: -lambda^3 + 6*lambda^2 - 10*lambda + 4 = 0

Eigenvalues: lambda = 2, 2+sqrt(2), 2-sqrt(2)
All positive => A is positive definite.

---

## 6. Important Properties

### For PD matrices:
- All eigenvalues > 0
- All leading principal minors > 0 (Sylvester's criterion)
- Matrix is invertible
- Matrix defines a valid covariance structure
- Cholesky decomposition exists: A = L * L^T

### For PSD matrices:
- All eigenvalues >= 0
- Matrix may be singular
- Used in kernel methods (kernel matrices are PSD)

### Connection to Optimization
- PD matrices ensure unique minimum in quadratic optimization
- Covariance matrices are always PSD
- Hessian being PD at critical point => local minimum
- Hessian being ND at critical point => local maximum

---

## 7. Applications in ML

| Concept | ML Application |
|---------|---------------|
| Eigenvalues/vectors | PCA dimensionality reduction |
| PD matrices | Kernel methods (Gram matrix must be PD) |
| PSD matrices | Covariance matrices in Gaussian models |
| Eigen decomposition | Spectral clustering |
| Quadratic forms | Loss functions (e.g., Mahalanobis distance) |
| Positive definiteness | Convergence guarantees in optimization |
