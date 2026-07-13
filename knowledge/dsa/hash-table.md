---
difficulty: medium
last_sent: null
review_count: 0
sequence: 2
tags:
- hash-table
- hashing
topic: dsa
---

# Hash Table

A hash table maps **keys to values** using a hash function to compute an index into an array of buckets. On average, insertions, deletions, and lookups are O(1). It's the backbone of dictionaries, sets, and frequency counters.

## Core operations

| Operation | Average | Worst | Notes |
|-----------|---------|-------|-------|
| Insert | O(1) | O(n) | Hash + handle collision |
| Lookup | O(1) | O(n) | Same as insert |
| Delete | O(1) | O(n) | Same as insert |
| Iterate all | O(n) | O(n) | Must visit every bucket |

## Hash function

A good hash function distributes keys uniformly across buckets. In practice, most languages handle this for you.

```python
# Python's built-in hash()
hash("hello")     # e.g., 1206987412
hash(42)          # 42
hash((1, 2, 3))  # hashable tuples only
```

The hash is then mapped to a bucket index: `index = hash(key) % capacity`.

## Collision handling: chaining

Each bucket holds a linked list (or dynamic array) of entries that hash to the same index.

```python
class HashTableChaining:
    def __init__(self, capacity=16):
        self.capacity = capacity
        self.size = 0
        self.buckets = [[] for _ in range(capacity)]

    def _hash(self, key):
        return hash(key) % self.capacity

    def put(self, key, value):
        idx = self._hash(key)
        bucket = self.buckets[idx]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self.size += 1
        if self.size / self.capacity > 0.75:
            self._resize()

    def get(self, key):
        idx = self._hash(key)
        for k, v in self.buckets[idx]:
            if k == key:
                return v
        raise KeyError(key)

    def delete(self, key):
        idx = self._hash(key)
        bucket = self.buckets[idx]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket.pop(i)
                self.size -= 1
                return
        raise KeyError(key)

    def _resize(self):
        old = self.buckets
        self.capacity *= 2
        self.buckets = [[] for _ in range(self.capacity)]
        self.size = 0
        for bucket in old:
            for k, v in bucket:
                self.put(k, v)
```

## Collision handling: open addressing

All entries stored in the array itself. On collision, probe for the next open slot.

### Linear probing

```python
class HashTableLinear:
    def __init__(self, capacity=16):
        self.capacity = capacity
        self.keys = [None] * capacity
        self.values = [None] * capacity
        self.size = 0

    def _hash(self, key):
        return hash(key) % self.capacity

    def put(self, key, value):
        if self.size / self.capacity > 0.7:
            self._resize()
        idx = self._hash(key)
        while self.keys[idx] is not None:
            if self.keys[idx] == key:
                self.values[idx] = value
                return
            idx = (idx + 1) % self.capacity
        self.keys[idx] = key
        self.values[idx] = value
        self.size += 1

    def get(self, key):
        idx = self._hash(key)
        while self.keys[idx] is not None:
            if self.keys[idx] == key:
                return self.values[idx]
            idx = (idx + 1) % self.capacity
        raise KeyError(key)

    def _resize(self):
        old_keys, old_values = self.keys, self.values
        self.capacity *= 2
        self.keys = [None] * self.capacity
        self.values = [None] * self.capacity
        self.size = 0
        for k, v in zip(old_keys, old_values):
            if k is not None:
                self.put(k, v)
```

## Load factor

**Load factor = n / capacity** (number of entries / number of buckets).

- Chaining: works well up to load factor ~1.0 (each bucket has ~1 element on average)
- Open addressing: must keep load factor low (typically < 0.7) to avoid long probe chains
- When load factor exceeds threshold, resize (double capacity and rehash everything)

## Frequency counting pattern

The most common use of hash tables in DSA problems.

```python
from collections import Counter

def top_k_frequent(nums, k):
    freq = Counter(nums)
    return [x for x, _ in freq.most_common(k)]

def two_sum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        complement = target - x
        if complement in seen:
            return [seen[complement], i]
        seen[x] = i
```

## Group anagrams

```python
from collections import defaultdict

def group_anagrams(strs):
    groups = defaultdict(list)
    for s in strs:
        key = tuple(sorted(s))  # or use char-count tuple
        groups[key].append(s)
    return list(groups.values())
```

## Hashing patterns in contests

| Pattern | Example |
|---------|---------|
| Frequency map | Count occurrences, find mode |
| Two-sum lookup | Check complement in O(1) |
| Grouping | Anagrams, equal rows/columns |
| Set operations | Intersection, union, difference |
| Sliding window + map | Longest substring with K distinct |
| Hashing for equality | Compare objects by computed signature |

## Common bugs

- Using mutable objects (lists, dicts) as hash keys — Python requires hashable types
- Ignoring load factor — hash table degrades to O(n) when too full
- Not handling deleted entries properly in open addressing (use tombstones)
- Assuming hash maps are ordered — use `OrderedDict` or `dict` (Python 3.7+ maintains insertion order)
- Hash collisions causing unexpected O(n) behavior on adversarial inputs

## Time/space

- Average: **O(1)** for insert, lookup, delete
- Worst case: **O(n)** when all keys hash to the same bucket
- Space: **O(n)** for storing entries, plus overhead for empty buckets
- Resize: **O(n)** amortized when triggered (happens rarely)