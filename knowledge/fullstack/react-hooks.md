---
difficulty: medium
last_sent:
review_count: 0
tags:
  - react
  - hooks
topic: fullstack
---

# React Hooks

Hooks let you use state and lifecycle features in function components. They replace class component patterns with a simpler, composable API. Hooks must follow the Rules of Hooks: only call at the top level, and only from React functions.

## useState

Manages local component state with re-render on change.

```jsx
import { useState } from "react";

function Counter() {
  const [count, setCount] = useState(0);

  return (
    <button onClick={() => setCount(c => c + 1)}>
      Clicked {count} times
    </button>
  );
}
```

### Lazy Initialization

```jsx
// Only computes on first render
const [state, setState] = useState(() => {
  const expensive = computeExpensiveValue();
  return expensive;
});
```

### Functional Updates

Always use the callback form when the new state depends on the previous state.

```jsx
// Correct — always reads latest state
setCount(prev => prev + 1);

// May use stale state in async callbacks
setCount(count + 1);
```

## useEffect

Side effects: data fetching, subscriptions, DOM manipulation. Runs after render.

```jsx
import { useState, useEffect } from "react";

function UserProfile({ userId }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    let cancelled = false;
    async function fetchUser() {
      const res = await fetch(`/api/users/${userId}`);
      const data = await res.json();
      if (!cancelled) setUser(data);
    }
    fetchUser();
    return () => { cancelled = true; }; // cleanup
  }, [userId]); // re-run when userId changes

  if (!user) return <p>Loading...</p>;
  return <h1>{user.name}</h1>;
}
```

### Dependency Array Rules

- **No array**: Runs after every render (usually unintentional).
- **Empty array `[]`**: Runs once on mount, cleanup on unmount.
- **With deps `[a, b]`**: Runs when `a` or `b` changes.

## useContext

Reads from a Context without prop drilling.

```jsx
const ThemeContext = createContext("light");

function App() {
  return (
    <ThemeContext.Provider value="dark">
      <Toolbar />
    </ThemeContext.Provider>
  );
}

function Toolbar() {
  const theme = useContext(ThemeContext);
  return <div className={theme}>Hello</div>;
}
```

`useContext` re-renders the component whenever the context value changes. For high-frequency updates, combine with `useMemo` or split contexts.

## useMemo and useCallback

**`useMemo`** caches an expensive computed value.

```jsx
const sortedItems = useMemo(() => {
  return items.sort((a, b) => a.name.localeCompare(b.name));
}, [items]);
```

**`useCallback`** caches a function reference to prevent unnecessary child re-renders.

```jsx
const handleClick = useCallback((id) => {
  setSelected(id);
}, []);

// Without useCallback: new function every render, child re-renders even if memo
// With useCallback: stable reference, child memo works
```

### When NOT to memoize

- Values that are cheap to compute — memoization itself has overhead.
- Functions passed to non-memoized children — the reference won't prevent re-renders anyway.
- State setters from `useState` — already stable by default.

## useRef

Mutable reference that persists across renders without causing re-renders.

```jsx
function Timer() {
  const intervalRef = useRef(null);
  const [count, setCount] = useState(0);

  useEffect(() => {
    intervalRef.current = setInterval(() => {
      setCount(c => c + 1);
    }, 1000);
    return () => clearInterval(intervalRef.current);
  }, []);

  return <p>Count: {count}</p>;
}
```

Also used to access DOM elements:

```jsx
function TextInput() {
  const inputRef = useRef(null);
  return (
    <>
      <input ref={inputRef} />
      <button onClick={() => inputRef.current.focus()}>Focus</button>
    </>
  );
}
```

## Custom Hooks

Extract reusable logic into functions prefixed with `use`.

```jsx
function useFetch(url) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetch(url)
      .then(res => res.json())
      .then(data => { if (!cancelled) setData(data); })
      .catch(err => { if (!cancelled) setError(err); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [url]);

  return { data, error, loading };
}

// Usage
function UserProfile({ id }) {
  const { data: user, loading, error } = useFetch(`/api/users/${id}`);
  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;
  return <h1>{user.name}</h1>;
}
```

## Rules of Hooks

1. **Only call at the top level** — never inside loops, conditions, or nested functions. This ensures hooks are called in the same order every render.
2. **Only call from React functions** — regular components or custom hooks. Never from plain JS functions, event handlers, or `setTimeout` callbacks.

## Common Bugs

- **Missing dependency in useEffect**: Stale closures read old values. Use the `exhaustive-deps` ESLint rule to catch this.
- **Infinite re-renders**: Creating objects/arrays/functions in the render and passing them as deps causes infinite loops. Memoize them.
- **Cleanup not returning a function**: `useEffect(() => { subscribe(); })` — the subscribe is never cleaned up. Must return `() => unsubscribe()`.
- **Conditional hooks**: `if (condition) { useState(...) }` breaks hook ordering. Move the condition inside the hook body.
- **`useEffect` vs `useLayoutEffect`**: `useLayoutEffect` blocks painting—use only for DOM measurements. For most side effects, `useEffect` is correct.

## Time/Space

- `useState`: O(1) per hook slot. React maintains a linked list of hook states per component.
- `useMemo`/`useCallback`: O(1) cache per dependency array. Overhead is ~5–10% compared to raw computation for trivial functions.
- `useContext` re-renders: Every component using `useContext(X)` re-renders when any value of `X` changes. For high-frequency updates, consider splitting context or using a state management library.
- Custom hooks have zero runtime overhead beyond the hooks they call internally.
