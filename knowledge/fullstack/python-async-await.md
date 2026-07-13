---
difficulty: hard
last_sent:
review_count: 0
tags:
  - python
  - async
topic: fullstack
---

# Python Async/Await

Async programming in Python allows concurrent execution of I/O-bound tasks without threads. The `async`/`await` syntax (introduced in Python 3.5+) provides a structured way to write single-threaded concurrent code using coroutines, driven by an event loop.

## Core Concepts

### Coroutines

A coroutine is a function defined with `async def`. It does not execute immediately—it returns a coroutine object that must be awaited or driven by an event loop.

```python
import asyncio

async def fetch_data(url: str) -> dict:
    print(f"Starting fetch from {url}")
    await asyncio.sleep(1)  # simulates I/O
    return {"url": url, "status": 200}

# Calling fetch_data() does NOT run it—it creates a coroutine object
coro = fetch_data("https://api.example.com")
```

### The Event Loop

The event loop is the scheduler that runs coroutines. It manages I/O events, callbacks, and coroutine execution.

```python
async def main():
    result = await fetch_data("https://api.example.com")
    print(result)

asyncio.run(main())  # Python 3.7+ — creates and closes the event loop
```

### Running Multiple Coroutines

```python
async def main():
    # Sequential — takes ~2 seconds
    r1 = await fetch_data("https://a.com")
    r2 = await fetch_data("https://b.com")

    # Concurrent — takes ~1 second
    r1, r2 = await asyncio.gather(
        fetch_data("https://a.com"),
        fetch_data("https://b.com"),
    )
```

## Key Primitives

### asyncio.gather

Runs multiple awaitables concurrently and returns results in order.

```python
results = await asyncio.gather(
    fetch_user(1),
    fetch_user(2),
    fetch_user(3),
)
```

### asyncio.create_task

Schedules a coroutine to run concurrently within the current event loop.

```python
async def main():
    task = asyncio.create_task(fetch_data("https://a.com"))
    # Do other work while fetch_data runs in background
    result = await task
```

### asyncio.Queue

Thread-safe async queue for producer-consumer patterns.

```python
async def producer(queue: asyncio.Queue):
    for i in range(10):
        await queue.put(i)
    await queue.put(None)  # sentinel

async def consumer(queue: asyncio.Queue):
    while True:
        item = await queue.get()
        if item is None:
            break
        print(f"Processing {item}")
```

### asyncio.Semaphore

Limits concurrent access to a resource.

```python
sem = asyncio.Semaphore(5)  # max 5 concurrent

async def limited_fetch(url: str):
    async with sem:
        return await fetch_data(url)
```

## Async Context Managers and Iterators

```python
class AsyncDBConnection:
    async def __aenter__(self):
        self.conn = await connect_db()
        return self.conn

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.conn.close()

async def query():
    async with AsyncDBConnection() as conn:
        return await conn.execute("SELECT 1")
```

## Async Generators

```python
async def async_range(n):
    for i in range(n):
        await asyncio.sleep(0.1)
        yield i

async def main():
    async for num in async_range(5):
        print(num)
```

## Async vs Threading

| Feature | `asyncio` | `threading` |
|---------|-----------|-------------|
| Best for | I/O-bound (network, disk) | I/O-bound or mixed |
| Memory overhead | Very low (~2KB per coroutine) | ~8MB per thread stack |
| CPU-bound work | Poor (blocks event loop) | OK (GIL released for I/O) |
| Complexity | Moderate (async ecosystem required) | Simpler for basic cases |
| Debugging | Harder (stack traces less intuitive) | Familiar to most devs |
| Scalability | Thousands to millions of coroutines | Hundreds to thousands of threads |

```python
# CPU-bound work: use ProcessPoolExecutor
from concurrent.futures import ProcessPoolExecutor

def cpu_heavy(n):
    return sum(i * i for i in range(n))

async def main():
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, cpu_heavy, 10_000_000)
```

## When to Use What

- **`asyncio`**: Network requests, database queries, file I/O with `aiofiles`, WebSocket connections, any high-concurrency I/O.
- **`threading`**: When libraries don't support async (blocking I/O wrappers), or for simple background tasks.
- **`multiprocessing`**: CPU-bound work that needs true parallelism.

## Common Bugs

- **Calling `await` outside async context**: `SyntaxError`—you must be inside `async def` or use `asyncio.run()`.
- **Blocking the event loop**: Calling `time.sleep()`, synchronous `requests.get()`, or heavy CPU work inside an async function blocks all concurrent tasks. Use `asyncio.sleep()` and `aiohttp` instead.
- **Forgetting `async with`/`async for`**: Async generators and context managers require their async variants; using `with` or `for` directly raises `TypeError`.
- **Fire-and-forget tasks**: Using `asyncio.create_task()` without keeping a reference can lead to silently garbage-collected tasks.

## Time/Space

- Coroutine creation: ~2KB memory vs ~8MB per OS thread.
- Event loop iteration: ~microseconds overhead per context switch.
- `asyncio.gather` with N tasks: O(N) space for result list; tasks run concurrently but event loop is single-threaded, so CPU-bound work still serializes.
