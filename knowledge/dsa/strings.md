---
difficulty: medium
last_sent: null
review_count: 0
tags:
- strings
topic: dsa
---

# Strings

Strings are **arrays of characters** with their own set of operations and algorithms. In Python, strings are immutable, so "modification" creates a new string. Many classic string problems reduce to array or hash map problems, but pattern matching has its own rich theory.

## String as character array

```python
s = "hello"
chars = list(s)         # ['h', 'e', 'l', 'l', 'o']
chars[0] = 'H'          # now mutable
result = "".join(chars)  # "Hello"
```

## Common operations

| Operation | Python | Time |
|-----------|--------|------|
| Concatenation | `s1 + s2` | O(n+m) |
| Substring | `s[start:end]` | O(end-start) |
| Search char | `s.find(ch)` | O(n) |
| Count | `s.count(sub)` | O(n*m) |
| Replace | `s.replace(old, new)` | O(n) |
| Split | `s.split(delim)` | O(n) |

## String hashing (Rabin-Karp concept)

Rolling hash enables O(n+m) substring search by comparing hash values instead of characters.

```python
def rabin_karp(text, pattern):
    n, m = len(text), len(pattern)
    base, mod = 31, 10**9 + 7

    # Hash of pattern
    pattern_hash = 0
    for ch in pattern:
        pattern_hash = (pattern_hash * base + ord(ch)) % mod

    # Rolling hash over text
    text_hash = 0
    power = pow(base, m - 1, mod)
    for i in range(n):
        text_hash = (text_hash * base + ord(text[i])) % mod
        if i >= m:
            text_hash = (text_hash - ord(text[i - m]) * power * base) % mod
        if i >= m - 1 and text_hash == pattern_hash:
            if text[i - m + 1:i + 1] == pattern:  # verify
                return i - m + 1
    return -1
```

## KMP concept (prefix function)

KMP avoids re-checking characters by precomputing a **failure function** (prefix table). If a mismatch occurs at position j, the table tells you where to jump next instead of restarting from scratch.

```python
def build_lps(pattern):
    """Longest Proper Prefix which is also Suffix array."""
    m = len(pattern)
    lps = [0] * m
    length = 0
    i = 1
    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        elif length > 0:
            length = lps[length - 1]
        else:
            lps[i] = 0
            i += 1
    return lps

def kmp_search(text, pattern):
    n, m = len(text), len(pattern)
    lps = build_lps(pattern)
    i = j = 0
    results = []
    while i < n:
        if text[i] == pattern[j]:
            i += 1
            j += 1
        if j == m:
            results.append(i - j)
            j = lps[j - 1]
        elif i < n and text[i] != pattern[j]:
            if j > 0:
                j = lps[j - 1]
            else:
                i += 1
    return results
```

## Anagram grouping

```python
from collections import defaultdict

def group_anagrams(words):
    groups = defaultdict(list)
    for w in words:
        key = tuple(sorted(w))  # or use char counts
        groups[key].append(w)
    return list(groups.values())
```

## Palindrome checks

```python
def is_palindrome(s):
    return s == s[::-1]

def longest_palindrome_substring(s):
    # Expand around center — O(n²)
    best = ""
    for center in range(len(s)):
        for left, right in [(center, center), (center, center + 1)]:
            while left >= 0 and right < len(s) and s[left] == s[right]:
                if right - left + 1 > len(best):
                    best = s[left:right + 1]
                left -= 1
                right += 1
    return best
```

## Common bugs

- Python strings are immutable: `s[i] = 'x'` raises an error — convert to list first
- Off-by-one in substring extraction: `s[i:j]` excludes index j
- Using `==` on large strings is O(n) — not free
- Forgetting case sensitivity or whitespace in string comparisons
- Building strings via `+=` in a loop is O(n²) — use `"".join()` instead

## Time/space

- Character access: **O(1)**
- Substring: **O(k)** where k is length
- KMP search: **O(n + m)** time, **O(m)** space
- Rabin-Karp: **O(n + m)** average, **O(nm)** worst case
- Space for strings: **O(n)** (immutable in Python, so concatenation creates copies)
