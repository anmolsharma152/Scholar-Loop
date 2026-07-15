---
difficulty: medium
last_sent: null
review_count: 0
sequence: 13
tags:
- tree
- traversal
topic: dsa
---

# Tree traversals

Visiting every node in a tree in a defined order. The three **depth-first** variants differ by when you visit the root relative to its children. **Level-order** (BFS) visits level by level. Each traversal has specific use cases — choosing the right one simplifies your code.

## Depth-first (recursive)

```python
def inorder(root):
    if not root: return
    inorder(root.left)
    print(root.val)       # visit
    inorder(root.right)

def preorder(root):
    if not root: return
    print(root.val)       # visit
    preorder(root.left)
    preorder(root.right)

def postorder(root):
    if not root: return
    postorder(root.left)
    postorder(root.right)
    print(root.val)       # visit
```

## Depth-first (iterative)

```python
def inorder_iter(root):
    stack, curr = [], root
    while stack or curr:
        while curr:
            stack.append(curr)
            curr = curr.left
        curr = stack.pop()
        print(curr.val)   # visit
        curr = curr.right

def preorder_iter(root):
    if not root: return
    stack = [root]
    while stack:
        node = stack.pop()
        print(node.val)   # visit
        if node.right: stack.append(node.right)
        if node.left: stack.append(node.left)
```

## Level-order (BFS)

```python
from collections import deque

def level_order(root):
    if not root: return []
    q, result = deque([root]), []
    while q:
        level = []
        for _ in range(len(q)):
            node = q.popleft()
            level.append(node.val)
            if node.left: q.append(node.left)
            if node.right: q.append(node.right)
        result.append(level)
    return result
```

## When to use each

| Traversal | Use case | Why |
|-----------|----------|-----|
| **Inorder** | Sorted output from BST | Left → Root → Right gives sorted order |
| **Preorder** | Clone / serialize a tree | Root first, then children — natural for reconstruction |
| **Postorder** | Delete tree, bottom-up DP | Children before parent — safe to delete |
| **Level-order** | Shortest path, print by level | BFS gives level-by-level processing |

## Common bugs

- Using a list as a queue (O(n) pop from front); use `collections.deque`
- Missing the `None` check before recursing — causes AttributeError
- Not resetting stack between traversals — state leaks
- Confusing inorder with preorder — BST inorder gives sorted; preorder doesn't

## Time/space

- Time: **O(n)** — each node visited once
- Space: **O(h)** for recursion stack / explicit stack, **O(n)** worst (skew); **O(w)** for BFS queue (w = max width)

## Quick reference

| Traversal | Mnemonic | Result for BST |
|-----------|----------|----------------|
| Inorder | Left → Root → Right | Sorted ascending |
| Preorder | Root → Left → Right | Root first, useful for copy |
| Postorder | Left → Right → Root | Root last, useful for delete |
| Level-order | Level by level | BFS order |