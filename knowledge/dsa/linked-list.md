---
difficulty: easy
last_sent: null
review_count: 0
tags:
  - linked-list
topic: dsa
---

# Linked list

A linear sequence of **nodes**, each holding a value and a pointer to the next node. Unlike arrays, elements are not stored contiguously; insertion and deletion are O(1) given a reference to the node.

## Singly linked list

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
```

Operations: traverse by following `next` until `None`. Insertion at head is O(1); deletion requires finding the previous node (O(n)).

## Doubly linked list

```python
class DListNode:
    def __init__(self, val=0, prev=None, next=None):
        self.val = val
        self.prev = prev
        self.next = next
```

Two pointers enable traversal in both directions. Deletion of a given node is O(1) since you have `prev`. Used in **LRU cache**.

## Circular linked list

The tail's `next` points back to the head (or some node). Useful for round-robin scheduling, Josephus problem. Detect with Floyd's cycle detection.

## Common patterns

| Pattern | Technique |
|---------|-----------|
| Reverse list | Three pointers (`prev`, `curr`, `next`) |
| Cycle detection | Slow/fast pointer (Floyd's) |
| Middle of list | Slow/fast pointer |
| Merge two sorted lists | Dummy head + compare |
| Remove nth from end | Two-pointer with gap of n |

## Common bugs

- Losing reference to the rest of the list when re-assigning `next`
- Forgetting to update the tail's `next` in a doubly linked list
- Off-by-one in reversal (not tracking `prev` correctly)
- Infinite loops from circular references

## Time/space

- Access by index: **O(n)**
- Insert/delete at head: **O(1)**
- Insert/delete at tail (singly): **O(n)** unless tail pointer kept
- Search: **O(n)**
- Space: **O(n)**
