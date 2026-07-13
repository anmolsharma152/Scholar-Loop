---
difficulty: hard
last_sent: null
review_count: 0
tags:
  - backtracking
  - recursion
topic: dsa
---

# Backtracking

A brute-force refinement that builds candidates incrementally and **abandons** a branch ("prunes") as soon as it cannot lead to a valid solution. The state-space tree represents all choices; backtracking does a DFS on this tree.

## Generic template

```python
def backtrack(candidate, state):
    if is_solution(candidate):
        add_to_result(candidate)
        return
    for choice in choices:
        if is_valid(choice, state):
            make_choice(choice, state)
            backtrack(candidate + [choice], state)
            undo_choice(choice, state)
```

## N-Queens

```python
def solve_n_queens(n):
    cols, diag1, diag2 = set(), set(), set()
    result = []

    def backtrack(row, board):
        if row == n:
            result.append(["".join(r) for r in board])
            return
        for col in range(n):
            if col in cols or (row - col) in diag1 or (row + col) in diag2:
                continue
            cols.add(col); diag1.add(row - col); diag2.add(row + col)
            board[row][col] = "Q"
            backtrack(row + 1, board)
            board[row][col] = "."
            cols.remove(col); diag1.remove(row - col); diag2.remove(row + col)

    backtrack(0, [["."] * n for _ in range(n)])
    return result
```

## Subsets / permutations / combinations

```python
def subsets(nums):
    result = []
    def backtrack(start, path):
        result.append(path[:])
        for i in range(start, len(nums)):
            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()
    backtrack(0, [])
    return result
```

Permutations differ by using a `used` array; combinations by controlling the start index.

## Classic problems

| Problem | Key pruning |
|---------|-------------|
| N-Queens | Column + diagonal conflict sets |
| Sudoku solver | Row/col/box sets per cell |
| Generate parentheses | `open < n` and `close < open` |
| Combination sum | Sort + skip duplicates; prune when sum exceeds target |
| Word search | Mark visited cells; prune out-of-bounds / mismatched |

## Common bugs

- Forgetting to undo the choice (state leaks across branches)
- Modifying a shared list in place without copying before storing
- Not sorting when duplicates need skipping
- Missing base case → infinite recursion

## Time/space

- Time: **O(branches^depth)** worst-case, but pruning cuts it significantly
- Space: **O(depth)** recursion stack + O(n) for result storage
