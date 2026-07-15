---
topic: fullstack
difficulty: medium
tags: [typescript, generics, advanced-types, patterns]
last_sent:
review_count: 0
---

# TypeScript Generics: Advanced Patterns

## Mapped Types

Transform properties of a type:
```typescript
type Readonly<T> = { readonly [K in keyof T]: T[K]; };
type Optional<T> = { [K in keyof T]?: T[K]; };
type Nullable<T> = { [K in keyof T]: T[K] | null; };
```

## Template Literal Types

```typescript
type EventName<T extends string> = `on${Capitalize<T>}`;
type ClickEvent = EventName<"click">;  // "onClick"
```

## Generic Classes

```typescript
class Stack<T> {
  private items: T[] = [];
  push(item: T): void { this.items.push(item); }
  pop(): T | undefined { return this.items.pop(); }
  peek(): T | undefined { return this.items[this.items.length - 1]; }
  get length(): number { return this.items.length; }
}
```

## Generic Utility Patterns

**Factory pattern:**
```typescript
function createInstance<T>(ctor: new (...args: any[]) => T, ...args: any[]): T {
  return new ctor(...args);
}
```

**Builder pattern:**
```typescript
class QueryBuilder<T> {
  private conditions: Partial<T> = {};
  where<K extends keyof T>(key: K, value: T[K]): this {
    this.conditions[key] = value;
    return this;
  }
}
```

**Discriminated unions in generics** for type-safe event handling:
```typescript
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };
```

## Best Practices

1. **Keep generics simple:** Start concrete; refactor to generic when reusable pattern emerges
2. **Avoid over-constraining:** `<T>` not `<T extends SomeSpecificInterface>` unless necessary
3. **Name clearly:** Use descriptive names like `TItem`, `TId` instead of single-letter names for complex cases
4. **Export generic types:** `export type ApiResponse<T> = ...` for library consumers
5. **Prefer generic functions over type assertions:** If you find yourself using `as`, consider if a generic would be safer
