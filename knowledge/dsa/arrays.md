---
difficulty: easy
last_sent: null
review_count: 0
tags:
- arrays
- matrix
topic: dsa
---

# Arrays

Arrays are the most fundamental data structure — a **contiguous block of memory** indexed by position. They provide O(1) random access and are the backbone of nearly every other data structure. Mastering array manipulation is essential before tackling any advanced topic.

## 1D arrays

Basic operations and their complexities:

| Operation | Time | Notes |
|-----------|------|-------|
| Access by index | O(1) | Direct memory offset |
| Search (unsorted) | O(n) | Must scan |
| Search (sorted) | O(log n) | Binary search |
| Insert at end (dynamic) | O(1) amortized | Resizing copies |
| Insert at position | O(n) | Shift elements |
| Delete at position | O(n) | Shift elements |

## Dynamic arrays (Python lists)

```python
# Amortized O(1) append
arr = []
arr.append(1)        # O(1) amortized
arr.append(2)
arr.insert(0, 0)     # O(n) — shifts everything

# List comprehension for quick creation
squares = [x * x for x in range(10)]

# Slicing creates a copy
copy = arr[:]
```

## Matrix (2D arrays)

```python
# Create m x n matrix
matrix = [[0] * n for _ in range(m)]

# Traverse row-major (standard)
for i in range(m):
    for j in range(n):
        process(matrix[i][j])

# Transpose (square matrix, in-place)
for i in range(n):
    for j in range(i + 1, n):
        matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
```

## Matrix rotation

### Rotate 90° clockwise

```python
def rotate_90(matrix):
    n = len(matrix)
    # Transpose then reverse each row
    for i in range(n):
        for j in range(i + 1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    for row in matrix:
        row.reverse()
```

### Rotate 90° counter-clockwise

```python
def rotate_ccw(matrix):
    n = len(matrix)
    # Transpose then reverse each column
    for i in range(n):
        for j in range(i + 1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    matrix.reverse()
```

## Spiral traversal

```python
def spiral_order(matrix):
    result = []
    while matrix:
        result += matrix.pop(0)           # top row
        if matrix and matrix[0]:
            for row in matrix:
                result.append(row.pop())  # right column
        if matrix:
            result += matrix.pop()[::-1]  # bottom row reversed
        if matrix and matrix[0]:
            for row in matrix[::-1]:
                result.append(row.pop(0)) # left column
    return result
```

## Kadane's algorithm (max subarray sum)

```python
def max_subarray(nums):
    best = current = nums[0]
    for x in nums[1:]:
        current = max(x, current + x)
        best = max(best, current)
    return best
```

## Common bugs

- Using `[[0] * n] * m` creates m references to the **same** row — mutations affect all rows
- Off-by-one in boundary checks: `range(n)` vs `range(n-1)`
- Forgetting that matrix.pop() modifies the original matrix (if you need the original, copy first)
- Integer overflow in subarray sum problems (not an issue in Python, but matters in Java/C++)

## Time/space

- Access: **O(1)**
- Search (unsorted): **O(n)**
- Search (sorted): **O(log n)**
- Insert/delete at position: **O(n)**
- Space: **O(n)** for 1D, **O(m×n)** for matrix
