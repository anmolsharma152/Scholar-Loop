---
difficulty: easy
last_sent: null
review_count: 0
tags:
- stack
topic: dsa
---

# Stack

A stack is a **LIFO (Last In, First Out)** data structure. The most recently added element is the first one removed. It's used everywhere — function call management, expression evaluation, undo operations, DFS traversal, and monotonic stack problems.

## Core operations

| Operation | Time | Description |
|-----------|------|-------------|
| push | O(1) | Add to top |
| pop | O(1) | Remove from top |
| peek/top | O(1) | View top without removing |
| isEmpty | O(1) | Check if empty |
| size | O(1) | Number of elements |

## Array-based stack (Python list)

```python
class Stack:
    def __init__(self):
        self.items = []

    def push(self, x):
        self.items.append(x)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[-1]

    def is_empty(self):
        return len(self.items) == 0
```

Python's list is a dynamic array — `append` and `pop` are O(1) amortized.

## Linked list stack

```python
class Node:
    def __init__(self, val, nxt=None):
        self.val = val
        self.next = nxt

class LinkedStack:
    def __init__(self):
        self.top = None
        self.size = 0

    def push(self, x):
        self.top = Node(x, self.top)
        self.size += 1

    def pop(self):
        val = self.top.val
        self.top = self.top.next
        self.size -= 1
        return val
```

Linked list gives guaranteed O(1) (no amortization), but uses more memory per element.

## Valid parentheses (classic)

```python
def is_valid(s):
    stack = []
    matching = {')': '(', ']': '[', '}': '{'}
    for ch in s:
        if ch in matching:
            if not stack or stack[-1] != matching[ch]:
                return False
            stack.pop()
        else:
            stack.append(ch)
    return len(stack) == 0
```

## Min stack (O(1) getMin)

```python
class MinStack:
    def __init__(self):
        self.stack = []
        self.min_stack = []  # mirrors stack with minimum at each level

    def push(self, x):
        self.stack.append(x)
        if not self.min_stack or x <= self.min_stack[-1]:
            self.min_stack.append(x)

    def pop(self):
        val = self.stack.pop()
        if val == self.min_stack[-1]:
            self.min_stack.pop()
        return val

    def get_min(self):
        return self.min_stack[-1]
```

## Infix to postfix (Shunting-yard algorithm)

Convert mathematical expressions from infix (a + b) to postfix (a b +) using a stack.

```python
def infix_to_postfix(expression):
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2}
    stack = []
    output = []
    tokens = expression.split()

    for token in tokens:
        if token.isalnum():
            output.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()  # remove '('
        else:
            while (stack and stack[-1] != '(' and
                   stack[-1] in precedence and
                   precedence[stack[-1]] >= precedence[token]):
                output.append(stack.pop())
            stack.append(token)

    while stack:
        output.append(stack.pop())

    return output
```

##单调栈 (Monotonic stack)

Maintains elements in increasing or decreasing order. Used for "next greater element" problems.

```python
def next_greater_element(nums):
    n = len(nums)
    result = [-1] * n
    stack = []
    for i in range(n):
        while stack and nums[stack[-1]] < nums[i]:
            result[stack.pop()] = nums[i]
        stack.append(i)
    return result
```

## Common bugs

- Calling `pop()` or `peek()` on an empty stack — always check `is_empty()` first
- Forgetting to handle unmatched opening parentheses
- Using a stack where a queue would be correct (or vice versa)
- Off-by-one when converting infix to postfix with unary operators

## Time/space

- All core operations: **O(1)**
- Infix to postfix: **O(n)** time, **O(n)** space
- Monotonic stack: **O(n)** time — each element is pushed and popped at most once
