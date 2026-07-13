---
difficulty: easy
last_sent: null
review_count: 0
tags:
  - tree
  - binary-tree
topic: dsa
---

# Binary tree

A **tree** where each node has **at most two children**: left and right. The top node is the **root**; nodes with no children are **leaves**. Edges connect parent to child. The **depth** of a node is the number of edges from the root; the **height** is the number of edges to the deepest leaf.

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

## Common bugs

- Confusing height vs depth
- Forgetting that a leaf node's children are `None`
- Treating an empty tree (`root is None`) as an edge case
- Assuming the tree is balanced when it might be a skew

## Time/space

- Access / search in an unbalanced tree: **O(n)** worst-case
- Access / search in a balanced tree: **O(log n)**
- Space: **O(n)** for storing n nodes
