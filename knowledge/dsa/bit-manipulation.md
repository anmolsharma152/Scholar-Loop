---
difficulty: medium
last_sent: null
review_count: 0
tags:
- bit-manipulation
- math
topic: dsa
---

# Bit Manipulation

Bit manipulation uses **individual bits of integers** to solve problems efficiently. Common in embedded systems, cryptography, and competitive programming. Many problems that seem to require extra space can be solved in O(1) space using bitwise tricks.

## Core operators

| Operator | Symbol | Example (5 & 3) | Result |
|----------|--------|------------------|--------|
| AND | `&` | `101 & 011` | `001` (1) |
| OR | `\|` | `101 \| 011` | `111` (7) |
| XOR | `^` | `101 ^ 011` | `110` (6) |
| NOT | `~` | `~0` | `-1` (two's complement) |
| Left shift | `<<` | `1 << 3` | `8` |
| Right shift | `>>` | `16 >> 2` | `4` |

## Essential tricks

### Check if bit i is set

```python
def is_set(n, i):
    return (n >> i) & 1 == 1
```

### Set bit i

```python
def set_bit(n, i):
    return n | (1 << i)
```

### Clear bit i

```python
def clear_bit(n, i):
    return n & ~(1 << i)
```

### Toggle bit i

```python
def toggle_bit(n, i):
    return n ^ (1 << i)
```

### Isolate lowest set bit

```python
lowest = n & (-n)  # works because -n is two's complement
```

### Clear lowest set bit

```python
n &= (n - 1)  # classic trick for counting bits
```

## Common patterns

### Find the single number (all others appear twice)

```python
def single_number(nums):
    result = 0
    for x in nums:
        result ^= x
    return result  # XOR cancels pairs
```

### Count set bits (Brian Kernighan's)

```python
def count_bits(n):
    count = 0
    while n:
        n &= (n - 1)  # clear lowest set bit
        count += 1
    return count
```

### Generate all subsets of a set

```python
def subsets(nums):
    n = len(nums)
    result = []
    for mask in range(1 << n):
        subset = [nums[i] for i in range(n) if mask & (1 << i)]
        result.append(subset)
    return result
```

### Swap without temp variable

```python
a ^= b
b ^= a
a ^= b
```

## Bitmask DP

Represent sets as integers for O(1) membership checks and O(n) iteration over subsets. Useful for TSP, assignment problems, and subset-sum variants.

```python
# Check if subset with bitmask m contains element i
def in_subset(m, i):
    return bool(m & (1 << i))
```

## Common bugs

- Shift by 32 or more bits is undefined behavior in some languages (mask with `& 0x31` or `& 63` for 32/64-bit)
- Signed right shift vs unsigned right shift: `>>` in Python is arithmetic (sign-extends), which is usually what you want
- Forgetting operator precedence: `(n & 1 << i)` parses as `n & (1 << i)`, not `(n & 1) << i`
- Using XOR swap when `a` and `b` refer to the same variable (a ^= a gives 0)

## Time/space

- Time: **O(1)** per bit operation, **O(32)** or **O(64)** for full integer scan
- Space: **O(1)** auxiliary
