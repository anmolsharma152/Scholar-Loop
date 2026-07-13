---
difficulty: medium
last_sent:
review_count: 0
tags:
  - javascript
  - async
topic: fullstack
---

# JavaScript Async Patterns

JavaScript is single-threaded and event-driven. Asynchronous patterns—callbacks, Promises, and async/await—allow non-blocking I/O by deferring work until the event loop processes the result.

## The Event Loop

The event loop continuously checks the call stack. When empty, it pulls from the microtask queue (higher priority), then the macrotask queue (lower priority).

```
Call Stack → Microtask Queue → Macrotask Queue → Render (if needed)
```

- **Microtasks**: `Promise.then/catch/finally`, `queueMicrotask`, `MutationObserver`
- **Macrotasks**: `setTimeout`, `setInterval`, `I/O callbacks`, `fetch` network response

```javascript
console.log("1");                        // Call stack
setTimeout(() => console.log("2"), 0);   // Macrotask
Promise.resolve().then(() => console.log("3")); // Microtask
console.log("4");
// Output: 1, 4, 3, 2
```

## Callbacks

The original async pattern. A function receives a callback to invoke when work completes.

```javascript
fs.readFile("data.json", "utf8", (err, data) => {
  if (err) {
    console.error("Failed:", err);
    return;
  }
  console.log("Data:", data);
});
```

### Callback Hell

Nesting multiple callbacks creates deeply indented, hard-to-maintain code.

```javascript
getUser(userId, (err, user) => {
  if (err) return handleError(err);
  getOrders(user.id, (err, orders) => {
    if (err) return handleError(err);
    getOrderDetails(orders[0].id, (err, details) => {
      if (err) return handleError(err);
      console.log(details);
    });
  });
});
```

## Promises

A Promise represents a value that may not be available yet. It has three states: pending, fulfilled, rejected.

```javascript
function fetchUser(id) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (id > 0) resolve({ id, name: "Alice" });
      else reject(new Error("Invalid ID"));
    }, 100);
  });
}

fetchUser(1)
  .then(user => console.log(user))
  .catch(err => console.error(err))
  .finally(() => console.log("Done"));
```

### Promise.all / allSettled / race / any

```javascript
// all: rejects immediately on first failure
const [users, posts] = await Promise.all([
  fetchUsers(),
  fetchPosts(),
]);

// allSettled: waits for all, never rejects
const results = await Promise.allSettled([fetchA(), fetchB()]);
// results: [{status: "fulfilled", value: ...}, {status: "rejected", reason: ...}]

// race: first to settle wins
const fastest = await Promise.race([fetchFromMirror1(), fetchFromMirror2()]);

// any: first to fulfill wins (ignores rejections until all fail)
const first = await Promise.any([fetchA(), fetchB()]);
```

### Chaining

```javascript
fetchUser(1)
  .then(user => fetchPosts(user.id))
  .then(posts => posts.length)
  .then(count => console.log(`${count} posts`))
  .catch(err => console.error(err));
```

Return values from `.then()` automatically wrap in resolved Promises, enabling chaining.

## async/await

Syntactic sugar over Promises that makes async code read like synchronous code.

```javascript
async function getUserPosts(userId) {
  try {
    const user = await fetchUser(userId);
    const posts = await fetchPosts(user.id);
    return posts.map(p => ({ ...p, author: user.name }));
  } catch (err) {
    console.error("Failed:", err);
    throw err;
  }
}
```

### Parallel with async/await

```javascript
// Sequential: ~2 seconds
const a = await fetchA();  // 1s
const b = await fetchB();  // 1s

// Parallel: ~1 second
const [a, b] = await Promise.all([fetchA(), fetchB()]);
```

### Top-Level await

```javascript
// In ES modules, you can use await at the top level
const response = await fetch("/api/data");
const data = await response.json();
```

## Common Async Patterns

### Debounce with Promise

```javascript
function debounce(fn, ms) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    return new Promise(resolve => {
      timer = setTimeout(() => resolve(fn(...args)), ms);
    });
  };
}
```

### Async Iteration

```javascript
async function* paginate(url) {
  let page = 1;
  while (true) {
    const res = await fetch(`${url}?page=${page}`);
    const data = await res.json();
    if (data.length === 0) break;
    yield* data;
    page++;
  }
}

for await (const item of paginate("/api/items")) {
  console.log(item);
}
```

## Common Bugs

- **Unhandled promise rejection**: Forgetting `.catch()` or `try/catch` with `await` causes silent failures. Use `process.on('unhandledRejection')` in Node.js to catch these.
- **Sequential when parallel**: Using `await` in a loop makes requests sequential. Use `Promise.all()` for independent operations.
- **Race conditions**: Two async operations writing to the same state without coordination. Use mutexes or sequential queues.
- **`forEach` with async**: `array.forEach(async item => await ...)` doesn't actually await—use `for...of` or `Promise.all(array.map(...))`.
- **Forgetting to return from `.then()`**: A `.then()` without a return breaks the chain, resulting in `undefined` for subsequent handlers.

## Time/Space

- Microtasks execute before the next macrotask—promises resolve faster than `setTimeout(..., 0)`.
- `Promise.all` with N promises: O(N) space for result array, time is max(individual times).
- `async/await` adds minimal overhead (~microseconds per await) vs raw Promises.
- Event loop starvation: A tight loop of microtasks (recursive promise resolution) blocks macrotasks including I/O and UI rendering.
