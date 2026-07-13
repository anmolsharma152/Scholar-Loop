---
difficulty: hard
last_sent: null
review_count: 0
sequence: 17
tags:
- dp
- knapsack
topic: dsa
---

# 0/1 Knapsack and variants

Given items with weights and values, what's the maximum value you can fit in a knapsack of capacity W? **0/1 knapsack**: each item taken at most once. **Unbounded knapsack**: each item can be taken any number of times. Subset sum and partition equal subset sum are special cases.

## 0/1 knapsack — 1D DP

```python
def knapsack(weights, values, W):
    n = len(weights)
    dp = [0] * (W + 1)
    for i in range(n):
        # iterate backwards to avoid reusing the same item
        for w in range(W, weights[i] - 1, -1):
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
    return dp[W]
```

## Unbounded knapsack

Same as above but iterate forward so items can be reused:

```python
def unbounded_knapsack(weights, values, W):
    dp = [0] * (W + 1)
    for w in range(1, W + 1):
        for i in range(len(weights)):
            if weights[i] <= w:
                dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
    return dp[W]
```

## Subset sum

```python
def subset_sum(nums, target):
    dp = [False] * (target + 1)
    dp[0] = True
    for num in nums:
        for s in range(target, num - 1, -1):
            if dp[s - num]:
                dp[s] = True
    return dp[target]
```

## Classic problems

| Problem | Variant |
|---------|---------|
| Partition equal subset sum | Subset sum to target = total/2 |
| Target sum | Subset sum: count ways to reach target |
| Coin change (fewest coins) | Unbounded knapsack, minimize count |
| Coin change II (ways) | Unbounded knapsack, count ways |
| Ones and zeros | 2D knapsack (two capacity dimensions) |

## Common bugs

- Iterating forward in 0/1 knapsack (turns it into unbounded)
- Wrong initialization: use `-inf` for exact-capacity problems, `0` for at-most-capacity
- Forgetting to handle the case where target sum is odd (can't partition equally)
- Off-by-one in capacity loop bounds

## Time/space

- Time: **O(n × W)** — n items, capacity W
- Space: **O(W)** — 1D DP array (can be O(n × W) for 2D)