---
created: '2026-07-16'
difficulty: easy
tags:
- python
- numpy
- arrays
topic: fullstack
---

# NumPy Fundamentals

NumPy is the foundation of scientific computing in Python. Pandas, scikit-learn, TensorFlow — all built on NumPy arrays.

## Why NumPy Over Lists

- **Homogeneous**: all elements same type → no type-checking overhead
- **Contiguous memory**: cache-friendly, vectorized operations
- **Broadcasting**: operations work on entire arrays without loops

```python
import numpy as np

# Python list: element-wise multiply requires a loop
python_list = [1, 2, 3]
result = [x * 2 for x in python_list]

# NumPy: vectorized
arr = np.array([1, 2, 3])
result = arr * 2  # array([2, 4, 6])
```

## Creating Arrays

```python
# From lists
np.array([1, 2, 3])                    # 1D
np.array([[1, 2], [3, 4]])             # 2D

# From scratch
np.zeros((3, 4))                       # 3x4 zeros
np.ones((2, 3))                        # 2x3 ones
np.random.random((5, 5))               # 5x5 random [0,1)
np.arange(0, 10, 2)                    # [0, 2, 4, 6, 8]
np.linspace(0, 1, 5)                   # 5 evenly spaced in [0,1]
np.full((3, 3), 7)                     # 3x3 filled with 7
```

## Array Attributes

```python
arr = np.array([[1, 2, 3], [4, 5, 6]])

arr.shape       # (2, 3) — rows x columns
arr.ndim        # 2 — number of dimensions
arr.size        # 6 — total elements
arr.dtype       # int64 — data type
arr.T           # Transpose: (3, 2)
```

## Indexing and Slicing

```python
arr = np.array([[1, 2, 3],
                [4, 5, 6],
                [7, 8, 9]])

arr[0, 1]       # 2 — row 0, col 1
arr[1, :]       # [4, 5, 6] — row 1
arr[:, 2]       # [3, 6, 9] — column 2
arr[0:2, 1:3]   # [[2, 3], [5, 6]] — submatrix
```

## Reshaping

```python
arr = np.arange(12)
arr.reshape(3, 4)       # 3x4 matrix
arr.reshape(2, 2, 3)    # 3D: 2 blocks of 2x3
arr.flatten()            # Back to 1D
```

Rule: total elements must match. `(12,)` can become `(3,4)`, `(2,6)`, `(2,2,3)` — not `(3,3)`.

## Vectorized Operations

```python
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

a + b           # [5, 7, 9]
a * b           # [4, 10, 18]
a @ b           # 32 (dot product)
np.dot(a, b)    # 32
```

**Aggregations:**
```python
arr = np.array([[1, 2], [3, 4]])

arr.mean()      # 2.5
arr.sum()       # 10
arr.std()       # 1.118
arr.min()       # 1
arr.max(axis=0) # [3, 4] — max along columns
arr.sum(axis=1) # [3, 7] — sum along rows
```

## Broadcasting

Arrays with different shapes can operate together:

```python
arr = np.array([[1, 2, 3],
                [4, 5, 6]])  # shape (2, 3)

# Subtract column means (shape (2,3) - shape (3,))
col_means = arr.mean(axis=0)   # [2.5, 3.5, 4.5]
centered = arr - col_means     # Each column centered to 0
```

## Key Takeaways

- NumPy arrays are homogeneous — faster and more memory-efficient than lists
- Use `np.zeros`, `np.ones`, `np.arange`, `np.linspace` to create arrays
- `reshape` requires total elements to match; `flatten` goes back to 1D
- Aggregations accept `axis` — `axis=0` collapses rows (operates on columns)
- Broadcasting lets you operate on arrays of different shapes without loops
