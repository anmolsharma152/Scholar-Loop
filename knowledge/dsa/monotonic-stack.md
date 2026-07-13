---
difficulty: hard
last_sent: null
review_count: 0
sequence: 10
tags:
- stack
- monotonic-stack
topic: dsa
---

# Monotonic stack

A stack whose elements are **strictly increasing or decreasing** when read from bottom to top. Used to find the **next greater/smaller element** in O(n) instead of O(n²). The core idea: when a new element breaks the monotonic property, pop elements off the stack — those popped elements have found their "next" element.

## Two types

### 1. Monotonically increasing stack (next smaller element)

Elements are in increasing order. When a smaller element arrives, pop everything larger — the smaller element is the *next smaller* for those popped.

```python
def next_smaller_element(nums):
    stack = []
    result = [-1] * len(nums)
    for i, val in enumerate(nums):
        while stack and nums[stack[-1]] > val:
            idx = stack.pop()
            result[idx] = val
        stack.append(i)
    return result
```

### 2. Monotonically decreasing stack (next greater element)

Elements are in decreasing order. When a larger element arrives, pop everything smaller — the larger element is the *next greater* for those popped.

```python
def next_greater_element(nums):
    stack = []
    result = [-1] * len(nums)
    for i, val in enumerate(nums):
        while stack and nums[stack[-1]] < val:
            idx = stack.pop()
            result[idx] = val
        stack.append(i)
    return result
```

## Classic problems

| Problem | Approach |
|---------|----------|
| Daily temperatures | Decreasing stack of indices; answer = i - popped_index |
| Largest rectangle in histogram | Increasing stack; height extends until a smaller bar appears |
| Trapping rain water | Decreasing stack; water trapped between popped bar and current |
| Next greater element I | Decreasing stack on nums2, store in map for nums1 |
| Sum of subarray minimums | Increasing stack, count contributions |

## Mental model

- The stack holds **indices** whose values are in monotonic order
- Popping means the current element is the "next" (greater or smaller) for the popped element
- The element left behind on the stack (or -1 if none) is the "previous"

## Common bugs

- Not distinguishing between strictly greater (`>`) vs greater-or-equal (`>=`)
- Forgetting to store indices instead of values when index distance matters
- Not processing remaining elements in the stack after the loop (they have no next element)
- Off-by-one in histogram — using a sentinel height 0 to flush the stack

## Time/space

- Time: **O(n)** — each element pushed and popped at most once
- Space: **O(n)** — stack holds at most n elements