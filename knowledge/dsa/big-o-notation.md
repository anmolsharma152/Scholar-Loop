---
difficulty: easy
last_sent: null
review_count: 0
sequence: 2
tags:
- complexity
- analysis
topic: dsa
---

# Big O Notation

Big O notation describes the **upper bound** of an algorithm's growth rate as input size increases. It lets us classify algorithms by their worst-case performance without worrying about hardware, constants, or lower-order terms. Understanding complexity analysis is the foundation for choosing the right data structure and algorithm.

## Three notations

| Notation | Meaning | Intuition |
|----------|---------|-----------|
| O(f(n)) | Upper bound | "At most this fast" |
| Θ(f(n)) | Tight bound | "Exactly this fast" |
| Ω(f(n)) | Lower bound | "At least this fast" |

In interviews and daily work, **Big O is king** — it tells you the worst-case ceiling. Big Theta is used when the best and worst cases match (e.g., merge sort is Θ(n log n)).

## Common complexities (best to worst)

| Big O | Name | Example |
|-------|------|---------|
| O(1) | Constant | Hash map lookup |
| O(log n) | Logarithmic | Binary search |
| O(n) | Linear | Single loop |
| O(n log n) | Linearithmic | Merge sort, heap sort |
| O(n²) | Quadratic | Nested loops |
| O(2ⁿ) | Exponential | Subset enumeration |
| O(n!) | Factorial | Permutation generation |

## Rules of thumb

1. **Drop constants**: O(2n) = O(n). Two passes through an array is still linear.
2. **Drop lower-order terms**: O(n² + n) = O(n²). The dominant term wins.
3. **Different inputs → different variables**: Two arrays of size n and m → O(n + m), not O(n).
4. **Loops multiply, conditions don't**: A loop inside a loop is O(n²); an if inside a loop is still O(n).

## Analyzing common patterns

```python
# O(1) — constant
def get_first(arr):
    return arr[0]

# O(n) — linear
def find_max(arr):
    best = arr[0]
    for x in arr:
        best = max(best, x)
    return best

# O(n²) — quadratic
def has_duplicate(arr):
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] == arr[j]:
                return True
    return False

# O(log n) — logarithmic
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```

## Recursive complexity

For `T(n) = aT(n/b) + O(n^d)`:
- If `log_b(a) < d` → O(n^d)
- If `log_b(a) == d` → O(n^d log n)
- If `log_b(a) > d` → O(n^(log_b(a)))

Examples: merge sort is `T(n) = 2T(n/2) + O(n)` → O(n log n). Binary search is `T(n) = T(n/2) + O(1)` → O(log n).

## Amortized analysis

Some operations are occasionally expensive but cheap on average. Dynamic array `append` is O(1) amortized — most appends are O(1), but occasional resize copies n elements across n total appends.

## Common bugs

- Confusing worst-case with average-case (e.g., quicksort is O(n²) worst but O(n log n) average)
- Forgetting that hash map operations are O(1) amortized, not O(1) guaranteed
- Counting output size as part of complexity (printing n items is O(n) output, not extra work)
- Treating recursion depth as time complexity instead of space

## Time/space

- This note is about **analyzing** time/space, not a single algorithm
- Space complexity counts auxiliary space, not input storage
- Stack space in recursion counts toward space complexity