---
difficulty: hard
last_sent: null
review_count: 0
sequence: 17
tags:
- dp
- dynamic-programming
topic: dsa
---

# Dynamic programming

Solving problems by breaking them into **overlapping subproblems**, solving each once, and storing the result. Two key properties: **optimal substructure** (optimal solution built from optimal solutions of subproblems) and **overlapping subproblems** (same subproblems recur).

## Memoization (top-down)

```python
def fib(n, memo={}):
    if n in memo: return memo[n]
    if n < 2: return n
    memo[n] = fib(n-1, memo) + fib(n-2, memo)
    return memo[n]
```

Recursive with caching. Easier to write; risk of stack overflow on deep recursion.

## Tabulation (bottom-up)

```python
def fib(n):
    if n < 2: return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]
```

Iterative array fill. No recursion overhead; can often optimize space to O(1).

## DP framework

1. **Define state** — what does `dp[i]` represent?
2. **Recurrence** — how does `dp[i]` relate to earlier states?
3. **Base case** — smallest subproblem
4. **Order** — iterate in an order that makes earlier states available
5. **Answer** — where in the DP table is the final answer?

## Classic patterns

| Pattern | Example | State |
|---------|---------|-------|
| 0/1 Knapsack | Pick items with weight ≤ W | `dp[i][w]` = max value using first i items |
| Unbounded knapsack | Coin change 2 | `dp[amount]` = number of ways |
| LIS | Longest increasing subsequence | `dp[i]` = LIS ending at i |
| LCS | Longest common subsequence | `dp[i][j]` = LCS of prefixes |
| Palindrome | Longest palindromic substring | `dp[i][j]` = is s[i..j] palindrome? |
| Grid DP | Min path sum | `dp[i][j]` = min cost to reach (i, j) |

## Common bugs

- Missing base case (infinite recursion or zeros)
- Wrong iteration order (needs careful thought for 1D vs 2D)
- Off-by-one in array indexing
- Forgetting that overlapping subproblems must exist (otherwise it's divide-and-conquer)
- State definition is too loose (combinatorial explosion) or too tight (misses subproblems)

## Time/space

- Time: number of states × cost per state transition
- Space: size of DP table (can often be optimized by keeping only the last few rows)