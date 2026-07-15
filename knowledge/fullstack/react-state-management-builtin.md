---
topic: fullstack
difficulty: medium
tags: [react, state-management, hooks]
last_sent:
review_count: 0
---

# React State Management: Built-in Tools

## useState

The simplest state primitive. Triggers re-render when state changes.

```typescript
const [count, setCount] = useState(0);
// Can be: value, function updater
setCount(prev => prev + 1);
// Lazy initializer (called once):
const [data] = useState(() => expensiveComputation());
```

**Key rule:** Don't call setState conditionally or in loops — it must be at the top level.

## useReducer

Better for complex state logic (multiple sub-values or next state depends on previous):

```typescript
const [state, dispatch] = useReducer(reducer, initialState);
// Action: { type: string, payload?: any }
function reducer(state: State, action: Action): State {
  switch(action.type) {
    case 'increment': return { count: state.count + 1 };
    default: return state;
  }
}
```

**When to use reducer over useState:** Multiple state values that change together, complex update logic, next state depends heavily on previous state.

## useRef

Holds mutable values that persist across renders without causing re-renders:

```typescript
const intervalRef = useRef<number | null>(null);
intervalRef.current = window.setInterval(() => {}, 1000);
```

Unlike state, mutating `ref.current` does NOT trigger re-render. Useful for DOM refs and interval/timeout IDs.

## Prop Drilling Problem

Passing props through multiple intermediate components that don't use them:

```typescript
<App>
  <Layout>
    <Main theme={theme} />  {/* Layout doesn't use theme */}
  </Layout>
</App>
```

**Solutions:** Context (below), component composition (lifting children to parent), or state management libraries.

## Context API

Share state across components without prop drilling:

```typescript
const ThemeContext = createContext('light');
function App() {
  return (
    <ThemeContext.Provider value="dark">
      <ThemedComponent />
    </ThemeContext.Provider>
  );
}
```

**Caveat:** Context value changes cause ALL consumers to re-render, not just the affected subtree. Split contexts by frequency of change.

## useMemo & useCallback

Optimize expensive computations and prevent unnecessary re-renders:

```typescript
const sorted = useMemo(() => expensiveSort(data), [data]);
const handleClick = useCallback(() => doThing(id), [id]);
```

**Key principle:** Don't optimize prematurely. Profile first. `useMemo`/`useCallback` themselves have overhead.
