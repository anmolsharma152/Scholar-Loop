---
difficulty: medium
last_sent:
review_count: 0
tags:
  - fastapi
  - di
topic: fullstack
---

# FastAPI Dependency Injection

Dependency injection (DI) in FastAPI lets you declare reusable components (dependencies) that are resolved automatically when a route is called. This is ideal for shared logic like authentication, database connections, pagination, and permission checks.

## Basic Dependencies

A dependency is any callable that FastAPI can inject into a route's parameters.

```python
from fastapi import Depends, FastAPI

app = FastAPI()

def common_dependency():
    return {"db": "connection"}

@app.get("/items")
def read_items(dep: dict = Depends(common_dependency)):
    return dep
```

When FastAPI calls `read_items`, it first calls `common_dependency()` and passes the result as `dep`.

## Class-Based Dependencies

Classes with `__init__` or `__call__` work as dependencies—useful for stateful or configurable dependencies.

```python
class Pagination:
    def __init__(self, page: int = 1, limit: int = 10):
        self.page = page
        self.limit = limit
        self.offset = (page - 1) * limit

@app.get("/items")
def list_items(pagination: Pagination = Depends()):
    return {"page": pagination.page, "offset": pagination.offset}

# Request: /items?page=2&limit=20 → pagination.page=2, pagination.limit=20
```

Query parameters from the request are automatically injected into the dependency's `__init__`.

## Auth Dependencies

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user

@app.get("/profile")
def profile(user = Depends(get_current_user)):
    return {"user_id": user.id, "email": user.email}
```

## Database Session Dependencies

```python
from contextlib import asynccontextmanager

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
```

Using `yield` makes this a dependency with cleanup. FastAPI runs the code after `yield` when the response is sent.

## Overriding Dependencies (Testing)

```python
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

def test_list_users():
    response = client.get("/users")
    assert response.status_code == 200
```

## Composing Dependencies

Dependencies can depend on other dependencies—FastAPI resolves the entire tree.

```python
def verify_admin(user = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, admin = Depends(verify_admin)):
    # get_current_user runs first, then verify_admin checks role
    return {"deleted": user_id}
```

## Caching Dependencies

By default, each dependency is called once per request, even if used in multiple places. For per-request caching across routes:

```python
from fastapi import Depends

async def get_user(user_id: int):
    print("Fetching user")  # runs only once per request
    return await db.get_user(user_id)

# Use CacheKeys or class-based approach for explicit caching
class DependsCache:
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, **kwargs):
        key = tuple(sorted(kwargs.items()))
        if key not in self.cache:
            self.cache[key] = self.func(**kwargs)
        return self.cache[key]
```

## Common Bugs

- **Forgetting `Depends()` parentheses**: `def route(dep = get_db)` passes the function itself, not its return value. Always use `Depends(get_db)`.
- **Side effects outside `yield`**: Code before `yield` in a dependency runs per-request. Code after `yield` runs on cleanup. Database connections must use `yield` for proper cleanup.
- **Dependency override not reset between tests**: `app.dependency_overrides` persists. Reset it in test teardown: `app.dependency_overrides.clear()`.
- **Circular dependencies**: A depends on B which depends on A—FastAPI will raise a runtime error on startup.

## Time/Space

- Dependency resolution adds negligible overhead (~microseconds) per call.
- `Depends()` without `use_cache=True` and `cache_per_request=False` ensures each injection point gets its own instance.
- Dependency tree depth is unbounded but practically < 10 levels. Very deep trees may slow startup slightly due to introspection.
