---
topic: fullstack
difficulty: medium
tags: [react, state-management, libraries]
last_sent:
review_count: 0
---

# React State Management: Libraries & Patterns

## When to Reach for a Library

- Deep component tree with many intermediate consumers
- State that's read/written by many distant components
- Performance-critical updates where Context triggers too many re-renders

## Zustand

Lightweight (~1KB), no boilerplate, minimal API:

```typescript
const useStore = create((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
}));
function Counter() {
  const count = useStore((state) => state.count);
  // Component only re-renders when count changes
}
```

**Advantages:** No provider wrapping needed, selector-based subscriptions prevent excess re-renders, works outside React.

## Redux Toolkit

Full-featured, best for large applications:

```typescript
const counterSlice = createSlice({
  name: 'counter',
  initialState: { value: 0 },
  reducers: {
    increment: (state) => { state.value += 1; },
  },
});
```

**Advantages:** DevTools, middleware ecosystem, RTK Query for data fetching. **Downside:** More boilerplate.

## React Query / TanStack Query

For server state (API data, caching):

```typescript
function Posts() {
  const { data, isLoading } = useQuery({
    queryKey: ['posts'],
    queryFn: () => fetch('/api/posts').then(r => r.json()),
  });
}
```

**Key insight:** Separates server state from UI state. Automatically handles caching, refetching, pagination, and optimistic updates.

## Atomic State (Jotai, Recoil)

Atom-based state management:

```typescript
const countAtom = atom(0);
const doubledAtom = atom((get) => get(countAtom) * 2);
```

**Advantages:** Fine-grained subscriptions, compositional (atoms derive from other atoms), no boilerplate.

## Decision Guide

| App Size | Approach |
|---|---|
| Tiny (1-3 pages) | useState + Context |
| Small (3-10 pages) | Zustand or Jotai |
| Medium (10-30 pages) | Zustand or RTK |
| Large (30+ pages) | Redux Toolkit + RTK Query |
| Server-heavy | React Query + local state library |
