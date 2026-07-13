---
difficulty: medium
last_sent:
review_count: 0
tags:
  - python
  - typing
topic: fullstack
---

# Python Type Hints

Type hints (PEP 484+) provide optional static type annotations for Python code. They don't affect runtime behavior but enable better IDE support, static analysis with tools like `mypy`, and clearer code documentation.

## Basic Types

```python
name: str = "Alice"
age: int = 30
price: float = 19.99
is_active: bool = True
items: list[int] = [1, 2, 3]       # Python 3.9+
mapping: dict[str, int] = {"a": 1}  # Python 3.9+
```

For older Python versions, use `typing.List`, `typing.Dict`, etc.

## Optional and Union

```python
from typing import Optional, Union

# Optional[X] is equivalent to Union[X, None] or X | None
def greet(name: Optional[str] = None) -> str:
    if name is None:
        return "Hello, stranger!"
    return f"Hello, {name}!"

# Union: accept multiple types
def process(value: Union[str, int]) -> str:
    return str(value)

# Python 3.10+ pipe syntax
def process(value: str | int) -> str:
    return str(value)
```

## Literal

Constrain a value to specific literal values rather than a general type.

```python
from typing import Literal

def set_mode(mode: Literal["read", "write", "append"]) -> None:
    ...

set_mode("read")    # OK
set_mode("delete")  # mypy error
```

## TypedDict

Define dictionaries with a fixed set of keys and value types—like a lightweight class without runtime overhead.

```python
from typing import TypedDict

class UserPayload(TypedDict):
    name: str
    age: int
    email: str

def create_user(data: UserPayload) -> None:
    print(f"Creating {data['name']}")

create_user({"name": "Alice", "age": 30, "email": "a@b.com"})  # OK
create_user({"name": "Alice"})  # mypy error: missing 'age' and 'email'
```

## Generics

Create reusable type-safe containers and functions.

```python
from typing import TypeVar, Generic

T = TypeVar("T")

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

int_stack: Stack[int] = Stack()
int_stack.push(42)
int_stack.pop()  # returns int
```

## Callable

```python
from typing import Callable

def apply(func: Callable[[int, int], int], a: int, b: int) -> int:
    return func(a, b)

apply(lambda x, y: x + y, 2, 3)  # 5
```

## Protocols (Structural Subtyping)

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...

class Circle:
    def draw(self) -> None:
        print("Drawing circle")

def render(shape: Drawable) -> None:
    shape.draw()

render(Circle())  # OK — Circle has .draw(), no inheritance needed
```

## NewType and TypeAlias

```python
from typing import NewType

UserId = NewType("UserId", int)
OrderId = NewType("OrderId", int)

def get_user(user_id: UserId) -> dict:
    ...

uid = UserId(42)
get_user(uid)       # OK
get_user(OrderId(42))  # mypy error: wrong NewType
```

## Generic Functions

```python
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")

def first(items: list[T]) -> T:
    return items[0]

def map_list(items: list[T], func: Callable[[T], R]) -> list[R]:
    return [func(item) for item in items]

result = map_list([1, 2, 3], str)  # list[str]
```

## Common Bugs

- **Using `list` instead of `list[int]`**: Bare `list` means `list[Any]`, losing type safety. Always parameterize generics.
- **`Optional` confusion**: Forgetting that `Optional[X]` includes `None`. A variable typed `Optional[str]` must be checked for `None` before calling `.upper()`.
- **Mutable default arguments**: `def f(x: list[int] = [])` is a type-level and runtime bug. Use `None` and assign inside.
- **Type narrowing failures**: After `if isinstance(x, str)`, mypy narrows the type, but with complex control flow it may not. Use `assert` or explicit casts when confident.
- **Overusing `Any`**: `Any` disables type checking. Use `object` or `Unknown` for truly unknown types.

## Time/Space

- Type hints add **zero runtime cost**—they are ignored by the interpreter (except in `get_type_hints()` and dataclass fields).
- `mypy --strict` on a 100k LOC project typically adds 5–15 seconds to CI.
- `TypedDict` has minimal runtime overhead (inherits from `dict`).
