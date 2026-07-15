---
difficulty: easy
last_sent: null
review_count: 0
sequence: 13
tags:
- tree
- binary-tree
topic: dsa
---

# Binary tree

A **tree** where each node has **at most two children**: left and right. The top node is the **root**; nodes with no children are **leaves**. Edges connect parent to child. The **depth** of a node is the number of edges from the root; the **height** is the number of edges to the deepest leaf. Binary trees are the foundation for BSTs, heaps, and tries.

## Terminology

| Term | Meaning |
|------|---------|
| **Root** | The node with no parent |
| **Leaf** | A node with no children |
| **Subtree** | Any node + its descendants |
| **Height** | Edges from root to deepest leaf |
| **Depth** | Edges from root to node |

## Structural types

| Type | Property |
|------|----------|
| **Full tree** | Every node has 0 or 2 children |
| **Complete tree** | All levels filled except possibly the last, which is left-packed |
| **Perfect tree** | All internal nodes have 2 children and all leaves at same depth |
| **Balanced tree** | Height difference between left and right subtrees ≤ 1 for every node |

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
```

## Why binary trees matter

Binary trees are the foundation for BSTs, heaps, and tries. Understanding them unlocks most tree-based data structures. A balanced BST gives O(log n) operations; a skewed tree degrades to O(n) linked list. Trees are used in databases (B-trees), compilers (ASTs), and networking (routing tables).

## Properties

- Maximum nodes at level l: 2^l
- Maximum nodes in tree of height h: 2^(h+1) - 1
- Minimum height with n nodes: floor(log2(n))
- In a full binary tree, number of leaf nodes = number of internal nodes + 1

## Common bugs

- Confusing height vs depth — height is bottom-up (edges to deepest leaf), depth is top-down (edges from root)
- Forgetting that a leaf node's children are `None` — always check before accessing
- Treating an empty tree (`root is None`) as an edge case — always check first in recursion
- Assuming the tree is balanced when it might be a skew — worst case is O(n) not O(log n)

## Time/space

- Access / search in an unbalanced tree: **O(n)** worst-case
- Access / search in a balanced tree: **O(log n)**
- Space: **O(n)** for storing n nodes