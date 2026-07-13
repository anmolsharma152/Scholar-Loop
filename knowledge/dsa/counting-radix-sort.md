---
difficulty: medium
last_sent: null
review_count: 0
tags:
  - sorting
topic: dsa
---

# Counting sort, radix sort & bucket sort

**Non-comparison sorts** that beat the O(n log n) lower bound by exploiting properties of the data. Work on integers or data that can be mapped to integers. Best used when the range of values is small relative to the number of elements.

## Counting sort

Count frequencies, compute prefix sums to determine positions, then place elements.

```python
def counting_sort(nums, k):
    """Sort nums where all values are in [0, k]."""
    count = [0] * (k + 1)
    for x in nums:
        count[x] += 1
    # prefix sums → positions
    for i in range(1, k + 1):
        count[i] += count[i - 1]
    output = [0] * len(nums)
    for x in reversed(nums):  # stable sort
        count[x] -= 1
        output[count[x]] = x
    return output
```

## Radix sort

Sort digit by digit from LSB to MSB using counting sort as the stable subroutine.

```python
def radix_sort(nums):
    max_val = max(nums)
    exp = 1
    while max_val // exp > 0:
        nums = counting_sort_by_digit(nums, exp)
        exp *= 10
    return nums
```

For negative numbers: separate negatives (sort absolute values, reverse), sort positives, concatenate negated + positives.

## Bucket sort

Distribute elements into buckets, sort each bucket individually, concatenate.

```python
def bucket_sort(nums, bucket_size=5):
    if not nums:
        return nums
    mn, mx = min(nums), max(nums)
    bucket_count = (mx - mn) // bucket_size + 1
    buckets = [[] for _ in range(bucket_count)]
    for x in nums:
        buckets[(x - mn) // bucket_size].append(x)
    result = []
    for b in buckets:
        result.extend(sorted(b))
    return result
```

## Classic problems

| Problem | Approach |
|---------|----------|
| Sort colors (Dutch flag) | Counting sort with k=2, or 3-way partition |
| Maximum gap | Bucket sort: min gap must span buckets |
| Sort an array of 0s, 1s, 2s | Counting sort or 3-way partition |
| Find the kth largest | Not sorting; QuickSelect. But radix + index lookup works |
| Sort by frequency | Bucket sort by frequency counts |

## Comparison

| Sort | When to use | Time | Space |
|------|-------------|------|-------|
| Counting | Small integer range, k = O(n) | O(n + k) | O(k) |
| Radix | Fixed-width integers, d digits | O(d × (n + k)) | O(n + k) |
| Bucket | Uniformly distributed data | O(n + m) avg, O(n²) worst | O(n + m) |

## Common bugs

- Counting sort: forgetting the stable reverse traversal
- Radix sort: not handling negative numbers
- Bucket sort: worst-case O(n²) when all elements land in one bucket
- Counting sort: allocating huge arrays when k is large (use dict instead)

## Time/space

- Counting sort: **O(n + k)** time, **O(k)** space (k = range)
- Radix sort: **O(d × (n + k))** time, **O(n + k)** space (d = digits, k = base)
- Bucket sort: **O(n + m)** avg time (m = buckets), **O(n)** extra space
