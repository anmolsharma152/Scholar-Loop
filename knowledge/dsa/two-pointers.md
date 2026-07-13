---
difficulty: medium
last_sent: null
review_count: 0
sequence: 11
tags:
- two-pointers
- arrays
topic: dsa
---

# Two Pointers

Two pointers is a pattern where you use **two indices** to traverse a data structure, typically reducing O(n²) brute force to O(n). The pointers can move toward each other, in the same direction, or from different starting points depending on the problem.

## When to reach for it

- Sorted arrays (two pointers naturally exploit sortedness)
- Pair/triplet problems (find pairs with a target sum)
- Palindrome checking (opposite ends moving inward)
- Removing duplicates in-place
- Merging sorted arrays

## Three main variants

### 1. Opposite ends (sorted array pair sum)

```python
def two_sum_sorted(arr, target):
    left, right = 0, len(arr) - 1
    while left < right:
        current = arr[left] + arr[right]
        if current == target:
            return [left, right]
        elif current < target:
            left += 1
        else:
            right -= 1
    return []
```

### 2. Same direction (fast/slow or slow/fast)

Used for removing duplicates, partitioning, and linked list cycle detection.

```python
def remove_duplicates(nums):
    """Remove duplicates in-place, return new length."""
    slow = 0
    for fast in range(1, len(nums)):
        if nums[fast] != nums[slow]:
            slow += 1
            nums[slow] = nums[fast]
    return slow + 1
```

### 3. Both start at same point (palindrome / container problems)

```python
def max_area(height):
    left, right = 0, len(height) - 1
    best = 0
    while left < right:
        area = min(height[left], height[right]) * (right - left)
        best = max(best, area)
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return best
```

## Three sum (classic pattern)

Sort first, then fix one element and use two pointers for the remaining pair.

```python
def three_sum(nums):
    nums.sort()
    result = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i - 1]:
            continue  # skip duplicates
        lo, hi = i + 1, len(nums) - 1
        while lo < hi:
            s = nums[i] + nums[lo] + nums[hi]
            if s < 0:
                lo += 1
            elif s > 0:
                hi -= 1
            else:
                result.append([nums[i], nums[lo], nums[hi]])
                while lo < hi and nums[lo] == nums[lo + 1]:
                    lo += 1
                while lo < hi and nums[hi] == nums[hi - 1]:
                    hi -= 1
                lo += 1
                hi -= 1
    return result
```

## Dutch National Flag (three-way partition)

Three pointers partition an array into three regions — used for sorting colors (0s, 1s, 2s).

```python
def sort_colors(nums):
    low, mid, high = 0, 0, len(nums) - 1
    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1
```

## Merging two sorted arrays

```python
def merge_sorted(a, b):
    result = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            result.append(a[i])
            i += 1
        else:
            result.append(b[j])
            j += 1
    result.extend(a[i:])
    result.extend(b[j:])
    return result
```

## Common bugs

- Not handling the case where the same element is used twice (check `lo != i` in three sum)
- Moving both pointers simultaneously when only one should move
- Forgetting to sort first when the problem requires it (pair sum on sorted array)
- Off-by-one with `left < right` vs `left <= right` (depends on whether you check single elements)

## Time/space

- Time: **O(n)** for most two-pointer problems, **O(n log n)** when sorting is needed
- Space: **O(1)** for in-place variants, **O(n)** if building a result array