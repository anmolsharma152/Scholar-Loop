---
difficulty: medium
last_sent:
review_count: 0
tags:
  - react
  - state
topic: fullstack
---

# React State Management

React's state management ranges from simple `useState` in individual components to global stores like Zustand. The right approach depends on how widely state is shared, how complex the updates are, and performance requirements.

## Local State with useState

For state that lives in a single component and doesn't need to be shared.

```jsx
function Toggle() {
  const [isOn, setIsOn] = useState(false);
  return (
    <button onClick={() => setIsOn(prev => !prev)}>
      {isOn ? "ON" : "OFF"}
    </button>
  );
}
```

Use when: form inputs, UI toggles, hover states, local data from a single API call.

## Lifting State Up

When two sibling components need to share state, move it to their closest common parent.

```jsx
function TemperatureCalculator() {
  const [celsius, setCelsius] = useState(0);

  return (
    <div>
      <TemperatureInput value={celsius} onChange={setCelsius} />
      <TemperatureDisplay celsius={celsius} />
    </div>
  );
}

function TemperatureInput({ value, onChange }) {
  return (
    <input
      type="number"
      value={value}
      onChange={e => onChange(Number(e.target.value))}
    />
  );
}

function TemperatureDisplay({ celsius }) {
  return <p>{celsius}°C = {celsius * 9/5 + 32}°F</p>;
}
```

## useReducer

For complex state logic involving multiple sub-values or transition-based updates.

```jsx
const initialState = { count: 0, step: 1 };

function reducer(state, action) {
  switch (action.type) {
    case "increment":
      return { ...state, count: state.count + state.step };
    case "decrement":
      return { ...state, count: state.count - state.step };
    case "setStep":
      return { ...state, step: action.payload };
    default:
      throw new Error(`Unknown action: ${action.type}`);
  }
}

function Counter() {
  const [state, dispatch] = useReducer(reducer, initialState);

  return (
    <div>
      <p>Count: {state.count}</p>
      <button onClick={() => dispatch({ type: "increment" })}>+</button>
      <button onClick={() => dispatch({ type: "decrement" })}>-</button>
      <input
        type="number"
        value={state.step}
        onChange={e => dispatch({ type: "setStep", payload: Number(e.target.value) })}
      />
    </div>
  );
}
```

`useReducer` is preferred when:
- State transitions depend on previous state in complex ways.
- Multiple related values change together.
- The reducer is easily testable as a pure function.

## Context API

Pass data through the component tree without prop drilling. Best for low-frequency updates (theme, auth, locale).

```jsx
const AuthContext = createContext(null);

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  const login = async (email, password) => {
    const res = await fetch("/api/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();
    setUser(data.user);
  };

  const logout = () => setUser(null);

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook for consuming
function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}
```

### Performance: Splitting Context

```jsx
// Bad: one context for everything → every consumer re-renders on any change
const AppContext = createContext({ user, theme, locale });

// Better: split by change frequency
const UserContext = createContext(user);     // changes on login/logout
const ThemeContext = createContext(theme);   // changes rarely
```

## Zustand

A minimal, fast state management library. No providers needed, works outside React.

```jsx
import { create } from "zustand";

const useStore = create((set, get) => ({
  count: 0,
  increment: () => set(state => ({ count: state.count + 1 })),
  decrement: () => set(state => ({ count: state.count - 1 })),
  reset: () => set({ count: 0 }),
  doubleIfEven: () => {
    const { count } = get();
    if (count % 2 === 0) set({ count: count * 2 });
  },
}));

function Counter() {
  const { count, increment, decrement } = useStore();
  return (
    <div>
      <p>{count}</p>
      <button onClick={increment}>+</button>
      <button onClick={decrement}>-</button>
    </div>
  );
}
```

### Selectors (Re-renders only on selected state)

```jsx
// Only re-renders when count changes, not when other state changes
const count = useStore(state => state.count);

// Zustand compares selectors shallowly by default
const { name, age } = useStore(state => ({ name: state.name, age: state.age }));
```

### Middleware

```jsx
import { persist } from "zustand/middleware";

const useStore = create(
  persist(
    (set) => ({
      count: 0,
      increment: () => set(state => ({ count: state.count + 1 })),
    }),
    { name: "counter-storage" } // localStorage key
  )
);
```

## Comparison

| Approach | Scope | Re-render Control | Complexity |
|----------|-------|-------------------|------------|
| `useState` | Component | Component only | Low |
| `useReducer` | Component | Component only | Low–Medium |
| Lifting state | Siblings | Parent + children | Low |
| Context | Tree | All consumers | Medium |
| Zustand | Global | Selector-based | Low |
| Redux | Global | Selector-based | High |

## When to Use What

- **`useState`**: Simple, local state. Start here.
- **`useReducer`**: Complex transitions, testable logic.
- **Lifting state**: 2–3 sibling components sharing data.
- **Context**: Theme, auth, locale—values that change infrequently.
- **Zustand**: Global app state (cart, notifications, user preferences) with fine-grained re-renders.
- **Redux/RTK**: Very large apps with complex side effects, many团队 developers, strict patterns.

## Common Bugs

- **Context re-render cascade**: A single context with a large value object causes all consumers to re-render when any property changes. Use `useMemo` on the provider value or split contexts.
- **Stale state in closures**: Event handlers capturing outdated state. Use functional updates (`setState(prev => prev + 1)`) or refs.
- **Over-memoizing**: Wrapping everything in `useMemo`/`useCallback` adds complexity without performance benefit. Profile before memoizing.
- **Missing `key` in lists**: Without unique keys, React can't efficiently reconcile list items, causing stale UI and broken state.

## Time/Space

- `useState` hook: O(1) space per state variable.
- Context re-renders: O(N) where N is the number of consumers—each re-renders on value change.
- Zustand selector re-render: O(1) — only the component with the changed selector re-renders.
- `useReducer` vs `useState`: Identical performance; `useReducer` is better for complex logic, not speed.
