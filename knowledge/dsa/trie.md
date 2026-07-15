---
difficulty: medium
last_sent: null
review_count: 0
sequence: 18
tags:
- trie
- string
topic: dsa
---

# Trie (prefix tree)

A tree-like data structure for **storing strings** where each node represents a prefix. Children are indexed by character (usually 26 for lowercase letters). Enables O(L) search, insert, and prefix lookup, where L is the string length — much faster than checking each string individually.

## Node structure

```python
class TrieNode:
    def __init__(self):
        self.children = {}      # char → TrieNode
        self.is_end = False     # marks end of a word
```

## Operations

```python
class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word):
        node = self._traverse(word)
        return node is not None and node.is_end

    def starts_with(self, prefix):
        return self._traverse(prefix) is not None

    def _traverse(self, s):
        node = self.root
        for ch in s:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node
```

## When to use a trie

| Problem | Why trie |
|---------|----------|
| Autocomplete / typeahead | Prefix search returns all words with given prefix |
| Word search on board (LeetCode 79) | Prune branches not in trie — massive speedup |
| Longest common prefix | Shallowest node with one child |
| Word break II | Check prefixes incrementally instead of all substrings |
| Replace words | Shortest prefix match — natural trie operation |

## Why not just use a set?

A HashSet can check exact words in O(L), but can't do prefix queries efficiently. Tries give you both: exact match (`search`) and prefix check (`starts_with`) in O(L). Use a trie when prefix operations matter.

## Space optimization

The basic trie can waste space with many single-child chains. A **compressed trie** (radix tree) merges chains into single edges, reducing space significantly. Patricia tries and suffix tries are common variants.

## Common bugs

- Not marking `is_end` after insert — search returns false for inserted words
- Confusing `search` (exact word) with `starts_with` (prefix match) — different semantics
- Using arrays of size 26 but forgetting to map characters to indices (`ord(ch) - ord('a')`)
- Not handling empty string input — empty string is a valid prefix

## Time/space

- Insert / Search / Prefix: **O(L)** where L is string length
- Space: **O(total characters stored)** — worst-case each char is a new node

## Trie vs HashSet

| Operation | HashSet | Trie |
|-----------|---------|------|
| Insert | O(L) | O(L) |
| Search exact | O(L) | O(L) |
| Prefix search | O(n*L) | O(L) |
| Delete | O(L) | O(L) |

Use trie when prefix operations matter; HashSet otherwise.