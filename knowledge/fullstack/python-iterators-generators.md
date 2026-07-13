---
difficulty: medium
last_sent: 2026-07-13 23:34:33.562385+00:00
review_count: 1
tags:
- python
- iterators
- generators
topic: fullstack
---

# Python Iterators and Generators

Iterables, iterators, and generators form Python's iteration protocol. Understanding them is key to writing memory-efficient data pipelines and custom collection types.

## Iterables vs Iterators

An **iterable** is any object with `__iter__()` that returns an iterator. An **iterator** is any object with both `__iter__()` and `__next__()`. `next()` calls `__next__()` on the iterator.

```python
class CountDown:
    def __init__(self, start: int):
        self.start = start

    def __iter__(self):
        return self

    def __next__(self) -> int:
        if self.start <= 0:
            raise StopIteration
        self.start -= 1
        return self.start + 1

for n in CountDown(5):
    print(n)  # 5, 4, 3, 2, 1
```

Key rules:
- Iterators are **exhausted** after one pass—they can only be iterated once.
- `for` loops call `iter()` on the iterable, then repeatedly call `next()` until `StopIteration`.
- Built-in `iter()` and `next()` are the public APIs for these dunder methods.

## Generators with yield

Generators are iterators created with `yield` instead of returning a list. Each `yield` produces a value and suspends the function.

```python
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

fib = fibonacci()
print(next(fib))  # 0
print(next(fib))  # 1
print(next(fib))  # 1

# Or iterate with a limit
from itertools import islice
print(list(islice(fibonacci(), 10)))
```

## Generator Functions vs Generator Expressions

```python
# Generator function
def squares(n: int):
    for i in range(n):
        yield i * i

# Generator expression (one-liner)
squares_gen = (i * i for i in range(10))

# Both produce the same sequence, but expressions are more concise
total = sum(i * i for i in range(1_000_000))  # single pass, O(1) memory
```

## Delegating Generators with yield from

`yield from` flattens nested iterables or delegates to sub-generators.

```python
def flatten(nested):
    for item in nested:
        if isinstance(item, (list, tuple)):
            yield from flatten(item)
        else:
            yield item

list(flatten([1, [2, [3, 4], 5], 6]))  # [1, 2, 3, 4, 5, 6]
```

## Generator Pipelines

Chain generators for efficient data processing without intermediate lists.

```python
def read_lines(filename):
    with open(filename) as f:
        for line in f:
            yield line.strip()

def filter_comments(lines):
    for line in lines:
        if not line.startswith("#"):
            yield line

def parse_csv(lines):
    for line in lines:
        yield line.split(",")

# Pipeline: read → filter → parse — O(1) memory for file I/O
pipeline = parse_csv(filter_comments(read_lines("data.csv")))
```

## Memory Efficiency Comparison

```python
import sys

# List: stores all 1M items in memory
list_comp = [i * i for i in range(1_000_000)]
print(sys.getsizeof(list_comp))  # ~8 MB

# Generator: stores only the current yield
gen_exp = (i * i for i in range(1_000_000))
print(sys.getsizeof(gen_exp))    # ~200 bytes (the generator object)
```

## itertools Utilities

```python
from itertools import chain, islice, accumulate, groupby, takewhile

# chain: concatenate iterables
combined = chain([1, 2], [3, 4])  # 1, 2, 3, 4

# islice: take first N items from a generator
first_5 = list(islice(fibonacci(), 5))  # [0, 1, 1, 2, 3]

# accumulate: running totals
running_sum = list(accumulate([1, 2, 3, 4]))  # [1, 3, 6, 10]

# takewhile: take while predicate is true
short = list(takewhile(lambda x: x < 5, [1, 3, 5, 2, 7]))  # [1, 3]
```

## Infinite Generators

Generators are ideal for infinite sequences since they produce values lazily.

```python
def cycle(iterable):
    saved = list(iterable)
    while True:
        yield from saved

colors = cycle(["red", "green", "blue"])
next(colors)  # "red"
next(colors)  # "green"
next(colors)  # "blue"
next(colors)  # "red" again
```

## Common Bugs

- **Exhausted iterator**: After iterating a generator once, it produces nothing on subsequent passes. Store as a list if reuse is needed.
- **Using `yield` inside list comprehensions**: `[yield x for x in range(5)]` creates a list of `None`—use a generator expression `(yield x ...)` or a plain generator function.
- **Returning a value in a generator**: `return value` in a generator sets `StopIteration.value` but the value is not yielded. Use `yield from` to retrieve it.
- **Unexpected laziness**: A generator doesn't compute until iterated. Side effects in generators may not run if the generator is never consumed.

## Time/Space

- Generator expression: O(1) space vs O(n) for list comprehension.
- `yield from` has minimal overhead (~10–20% slower than manual loop) but improves readability.
- `itertools.chain` is implemented in C and is near C-speed.
- Generator pipeline with N stages: O(1) total space, O(N) call stack depth per `next()` call.