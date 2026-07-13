---
difficulty: hard
last_sent: null
review_count: 0
tags:
  - dp
  - grid
topic: dsa
---

# DP on grids

Problems where you traverse a 2D grid from one corner to another, making decisions at each cell. Usually involves moving right/down (or all 4 directions in harder variants). State is `dp[r][c]`, the best value reachable at cell (r, c).

## Unique paths (top-left to bottom-right)

```python
def unique_paths(m, n):
    dp = [1] * n
    for _ in range(1, m):
        for c in range(1, n):
            dp[c] += dp[c - 1]
    return dp[-1]
```

## Minimum path sum

```python
def min_path_sum(grid):
    m, n = len(grid), len(grid[0])
    dp = [float('inf')] * n
    dp[0] = 0
    for r in range(m):
        for c in range(n):
            if c > 0:
                dp[c] = min(dp[c], dp[c - 1]) + grid[r][c]
            else:
                dp[c] = dp[c] + grid[r][c]
    return dp[-1]
```

## Maximal square

Find the largest square of 1s in a binary matrix. `dp[r][c]` = size of largest square ending at (r, c).

```python
def maximal_square(matrix):
    m, n = len(matrix), len(matrix[0])
    dp = [[0] * n for _ in range(m)]
    best = 0
    for r in range(m):
        for c in range(n):
            if matrix[r][c] == '1':
                if r == 0 or c == 0:
                    dp[r][c] = 1
                else:
                    dp[r][c] = min(dp[r-1][c], dp[r][c-1], dp[r-1][c-1]) + 1
                best = max(best, dp[r][c])
    return best * best
```

## Classic problems

| Problem | Twist |
|---------|-------|
| Unique paths II | Obstacles: skip blocked cells |
| Dungeon game | Backward DP from bottom-right to top-left |
| Cherry pickup | Two walks: 2 × 1D DP with step parity |
| Triangle (minimum path sum) | Triangular grid, space-optimized bottom-up |
| Count square submatrices with all ones | Same as maximal square, sum all dp values |
| Out of boundary paths | 3D DP (row, col, moves left); use modulo |

## Common bugs

- Not handling obstacles (`0` / `-1` initialization vs `inf`)
- Mixing up row and column indices
- Forgetting that dp values can overflow (use mod when required)
- Cherry pickup: not marking picked cherries as 0 for the second pass (use two 1D states keyed by steps)

## Time/space

- Time: **O(m × n)** — visit each cell once
- Space: **O(min(m, n))** or **O(m × n)** depending on problem
