---
difficulty: medium
last_sent: null
review_count: 0
sequence: 14
tags:
- bst
- tree
topic: dsa
---

# Binary search tree

A binary tree where for every node: all values in the **left** subtree are **less than** the node's value, and all values in the **right** subtree are **greater than** (or equal to, depending on variant). An inorder traversal yields values in **sorted order**.

## Search

```python
def search_bst(root, val):
    curr = root
    while curr:
        if val == curr.val: return curr
        elif val < curr.val: curr = curr.left
        else: curr = curr.right
    return None
```

## Insert

```python
def insert_bst(root, val):
    if not root: return TreeNode(val)
    if val < root.val:
        root.left = insert_bst(root.left, val)
    else:
        root.right = insert_bst(root.right, val)
    return root
```

## Delete

```python
def delete_bst(root, val):
    if not root: return None
    if val < root.val: root.left = delete_bst(root.left, val)
    elif val > root.val: root.right = delete_bst(root.right, val)
    else:
        if not root.left: return root.right
        if not root.right: return root.left
        # node with 2 children: find inorder successor
        succ = root.right
        while succ.left: succ = succ.left
        root.val = succ.val
        root.right = delete_bst(root.right, succ.val)
    return root
```

## Validate BST

```python
def is_valid_bst(root, lo=-inf, hi=inf):
    if not root: return True
    if not (lo < root.val < hi): return False
    return (is_valid_bst(root.left, lo, root.val) and
            is_valid_bst(root.right, root.val, hi))
```

## Classic problems

| Problem | Approach |
|---------|----------|
| Lowest common ancestor | Walk from root, branch according to values |
| Kth smallest | Inorder traversal (stop at k) |
| Convert sorted array to BST | Pick middle as root, recurse left/right |
| Two-sum in BST | Inorder → two-pointer on sorted array |
| Floor / Ceil | Track closest during search |

## Common bugs

- Forgetting that an inorder traversal alone may not validate BST (duplicates, out-of-range ancestors)
- Not passing min/max bounds when validating
- Returning wrong node after deletion (orphaning children)

## Time/space

- Search / Insert / Delete: **O(log n)** average, **O(n)** worst-case (skewed tree)
- Space: **O(h)** recursion stack