---
difficulty: medium
last_sent: null
review_count: 0
tags:
- sorting
- divide-and-conquer
topic: dsa
---

# Merge Sort

Merge sort is a **divide-and-conquer** sorting algorithm that splits the array in half, recursively sorts each half, and merges the results. It guarantees O(n log n) time in all cases and is stable, making it one of the most reliable general-purpose sorts.

## The algorithm

1. **Divide**: Split the array into two halves
2. **Conquer**: Recursively sort each half
3. **Combine**: Merge two sorted halves into one sorted array

```python
def merge_sort(arr):
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:  # <= makes it stable
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
```

## In-place merge sort

The standard version uses O(n) extra space per merge. An in-place merge is possible but complex — typically O(n) time with O(1) extra space using rotation-based techniques.

```python
def merge_sort_inplace(arr, left, right):
    if right - left <= 1:
        return
    mid = (left + right) // 2
    merge_sort_inplace(arr, left, mid)
    merge_sort_inplace(arr, mid, right)
    # For simplicity, use temporary array for merge
    temp = arr[left:mid]
    i, j, k = 0, mid, left
    while i < len(temp) and j < right:
        if temp[i] <= arr[j]:
            arr[k] = temp[i]
            i += 1
        else:
            arr[k] = arr[j]
            j += 1
        k += 1
    while i < len(temp):
        arr[k] = temp[i]
        i += 1
        k += 1
```

## Counting inversions

Merge sort can count inversions (pairs where i < j but arr[i] > arr[j]) during the merge step.

```python
def count_inversions(arr):
    if len(arr) <= 1:
        return arr, 0
    mid = len(arr) // 2
    left, inv_left = count_inversions(arr[:mid])
    right, inv_right = count_inversions(arr[mid:])
    merged, inv_split = merge_count(left, right)
    return merged, inv_left + inv_right + inv_split

def merge_count(left, right):
    result = []
    i = j = inversions = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            inversions += len(left) - i  # all remaining left elements are > right[j]
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result, inversions
```

## Bottom-up merge sort (iterative)

Avoids recursion by merging progressively larger subarrays.

```python
def merge_sort_iterative(arr):
    n = len(arr)
    width = 1
    while width < n:
        for i in range(0, n, width * 2):
            left = arr[i:i + width]
            right = arr[i + width:i + width * 2]
            merged = merge(left, right)
            arr[i:i + len(merged)] = merged
        width *= 2
    return arr
```

## Key properties

- **Stable**: Equal elements maintain their relative order
- **Guaranteed O(n log n)**: Unlike quicksort, no worst-case degradation
- **External sort**: Works well for data that doesn't fit in memory (sequential access pattern)
- **Linked list**: For linked lists, merge sort is O(1) extra space (no random access needed for split)

## Common bugs

- Using `<` instead of `<=` in merge breaks stability
- Creating too many intermediate lists in Python (each recursive call allocates)
- Forgetting to handle the remaining elements after the main merge loop
- Off-by-one in mid calculation: use `len(arr) // 2` (floor division)
- Not returning early for base case (`len(arr) <= 1`)

## Time/space

- Time: **O(n log n)** in all cases (best, average, worst)
- Space: **O(n)** for the standard implementation
- Inversions: **O(n log n)** time, **O(n)** space
