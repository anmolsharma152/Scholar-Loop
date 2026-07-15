---
difficulty: easy
last_sent: null
review_count: 0
sequence: 7
tags:
- linked-list
topic: dsa
---

# Linked list

A linear sequence of **nodes**, each holding a value and a pointer to the next node. Unlike arrays, elements are not stored contiguously in memory; insertion and deletion are O(1) given a reference to the node, but access by index is O(n).

## Singly linked list

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
```

Operations: traverse by following `next` until `None`. Insertion at head is O(1); deletion requires finding the previous node (O(n)). No random access — you must walk from the head.

## Doubly linked list

```python
class DListNode:
    def __init__(self, val=0, prev=None, next=None):
        self.val = val
        self.prev = prev
        self.next = next
```

Two pointers enable traversal in both directions. Deletion of a given node is O(1) since you have `prev`. Used in **LRU cache** (combined with HashMap for O(1) lookup). Extra memory per node for the prev pointer.

## Circular linked list

The tail's `next` points back to the head (or some node). Useful for round-robin scheduling, Josephus problem. Detect with Floyd's cycle detection (slow/fast pointers). No `None` terminator — watch for infinite loops.

## Common patterns

| Pattern | Technique |
|---------|-----------|
| Reverse list | Three pointers (`prev`, `curr`, `next`) — classic |
| Cycle detection | Slow/fast pointer (Floyd's) — O(n) time, O(1) space |
| Middle of list | Slow/fast pointer — slow reaches middle when fast reaches end |
| Merge two sorted lists | Dummy head + compare — clean and simple |
| Remove nth from end | Two-pointer with gap of n — one pass |

## Why linked lists over arrays?

Arrays give O(1) access but O(n) insertion/deletion. Linked lists give O(1) insertion/deletion (given reference) but O(n) access. Use linked lists when you need frequent insertions/deletions in the middle, like implementing a queue or LRU cache. Arrays are better for random access and cache locality.

## Common bugs

- Losing reference to the rest of the list when re-assigning `next` — always save the next node first
- Forgetting to update the tail's `next` in a doubly linked list — breaks traversal
- Off-by-one in reversal (not tracking `prev` correctly) — practice the three-pointer pattern
- Infinite loops from circular references — always have a termination condition or visited set

## Time/space

- Access by index: **O(n)**
- Insert/delete at head: **O(1)**
- Insert/delete at tail (singly): **O(n)** unless tail pointer kept
- Search: **O(n)**
- Space: **O(n)**