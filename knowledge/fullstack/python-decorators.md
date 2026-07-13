---
difficulty: medium
last_sent:
review_count: 0
tags:
  - python
  - decorators
topic: fullstack
---

# Python Decorators

Decorators are functions that modify other functions or classes without changing their source code. They leverage Python's first-class functions to wrap behavior around function calls, enabling clean separation of cross-cutting concerns like logging, authentication, caching, and timing.

## The @ Syntax

A decorator is any callable that takes a callable and returns a callable. The `@` syntax is syntactic sugar for function wrapping.

```python
import functools

def my_decorator(func):
    @functools.wraps(func)  # preserves __name__, __doc__, etc.
    def wrapper(*args, **kwargs):
        print("Before")
        result = func(*args, **kwargs)
        print("After")
        return result
    return wrapper

@my_decorator
def say_hello(name):
    """Say hello to someone."""
    print(f"Hello, {name}!")

say_hello("Alice")
# Before
# Hello, Alice!
# After
```

Without `@`, the equivalent is: `say_hello = my_decorator(say_hello)`.

## Common Use Cases

### Timing

```python
import time
import functools

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)

slow_function()  # slow_function took 1.0012s
```

### Authentication

```python
def require_auth(func):
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            raise PermissionError("Not authenticated")
        return func(request, *args, **kwargs)
    return wrapper

@require_auth
def dashboard(request):
    return "Welcome to your dashboard"
```

### Caching

```python
def memoize(func):
    cache = {}
    @functools.wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrapper

@memoize
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

Python's standard library provides `@functools.lru_cache` and `@functools.cache` for this purpose.

## Decorators with Arguments

```python
def retry(max_attempts=3, delay=1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise
                    print(f"Attempt {attempt} failed: {e}. Retrying...")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(max_attempts=5, delay=2)
def unstable_api_call():
    ...
```

## Stacking Decorators

```python
@timer
@require_auth
def protected_dashboard(request):
    ...
```

Execution order is bottom-up: `require_auth` wraps the function first, then `timer` wraps the result. So `timer` runs first.

## Class-Based Decorators

```python
class CountCalls:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"Call #{self.count} to {self.func.__name__}")
        return self.func(*args, **kwargs)

@CountCalls
def greet(name):
    print(f"Hi {name}")
```

## Common Bugs

- **Missing `@functools.wraps`**: Without it, the decorated function loses its name and docstring, breaking introspection and API docs (e.g., FastAPI route names).
- **Returning `None` accidentally**: If the wrapper forgets `return func(...)`, the original return value is lost.
- **Mutable default state**: Caching decorators that use a dict as default argument across calls share state unexpectedly.
- **Order matters**: Stacking decorators in the wrong order changes execution behavior—always reason from bottom to top.
