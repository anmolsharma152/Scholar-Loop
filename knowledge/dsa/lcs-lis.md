---
difficulty: hard
last_sent: null
review_count: 0
sequence: 17
tags:
- dp
- strings
topic: dsa
---

# Longest common subsequence & Longest increasing subsequence

Foundational DP problems on sequences. LCS finds the longest subsequence common to two strings. LIS finds the longest increasing subsequence in an array. Both are O(n²) in their classic forms, but LIS has an O(n log n) binary search variant.

## Longest common subsequence

```python
def lcs(text1, text2):
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = 1 + dp[i - 1][j - 1]
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]
```

## Longest increasing subsequence (O(n²))

```python
def lis(nums):
    n = len(nums)
    dp = [1] * n
    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)
```

## LIS in O(n log n)

Maintain an array `tails` where `tails[k]` is the smallest tail of an increasing subsequence of length k+1. Use binary search to find the position of each element.

```python
import bisect

def lis_fast(nums):
    tails = []
    for x in nums:
        idx = bisect.bisect_left(tails, x)
        if idx == len(tails):
            tails.append(x)
        else:
            tails[idx] = x
    return len(tails)
```

## Classic problems

| Problem | Relation |
|---------|----------|
| Edit distance | LCS variant: min operations to convert string A to B |
| Shortest common supersequence | m + n - LCS |
| Maximum length of pair chain | LIS on second element after sorting by first |
| Russian doll envelopes | 2D LIS: sort by width asc, height desc |
| Delete operation for two strings | m + n - 2 * LCS |
| Number of LIS | Track count alongside length in LIS DP |

## Common bugs

- LCS: using `max(dp[i-1][j], dp[i][j-1])` when chars match (should be `1 + dp[i-1][j-1]`)
- LIS: not allowing equal elements (`<` vs `<=`)
- LIS O(n log n): using `bisect_right` instead of `bisect_left` — breaks correctness for equal values
- Edit distance: forgetting the replace operation cost

## Time/space

- LCS: Time **O(m × n)**, Space **O(min(m, n))** with 1D optimization
- LIS O(n²): Time **O(n²)**, Space **O(n)**
- LIS O(n log n): Time **O(n log n)**, Space **O(n)**