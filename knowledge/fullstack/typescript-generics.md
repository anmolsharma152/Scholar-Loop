---
difficulty: hard
last_sent:
review_count: 0
tags:
  - typescript
  - generics
topic: fullstack
---

# TypeScript Generics

Generics let you write type-safe, reusable code that works with multiple types. They are the foundation of utility types, higher-order types, and complex type-level programming in TypeScript.

## Basic Generics

```typescript
// Generic function
function identity<T>(value: T): T {
  return value;
}

identity<string>("hello");  // explicit
identity(42);               // inferred as number

// Generic interface
interface Container<T> {
  value: T;
  getValue(): T;
}

const numBox: Container<number> = { value: 42, getValue() { return this.value; } };
```

## Constraints with extends

```typescript
// T must have a .length property
function logLength<T extends { length: number }>(item: T): T {
  console.log(item.length);
  return item;
}

logLength("hello");    // OK — string has .length
logLength([1, 2, 3]);  // OK — array has .length
logLength(42);         // Error — number has no .length

// keyof constraint
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

const user = { name: "Alice", age: 30 };
getProperty(user, "name");  // OK — returns string
getProperty(user, "email"); // Error — "email" not in keyof User
```

## Multiple Type Parameters

```typescript
function merge<T, U>(a: T, b: U): T & U {
  return { ...a, ...b };
}

function pick<T, K extends keyof T>(obj: T, keys: K[]): Pick<T, K> {
  const result = {} as Pick<T, K>;
  keys.forEach(k => { result[k] = obj[k]; });
  return result;
}
```

## Generic Classes

```typescript
class Stack<T> {
  private items: T[] = [];

  push(item: T): void {
    this.items.push(item);
  }

  pop(): T | undefined {
    return this.items.pop();
  }

  peek(): T | undefined {
    return this.items[this.items.length - 1];
  }

  get size(): number {
    return this.items.length;
  }
}

const numStack = new Stack<number>();
numStack.push(1);
numStack.push("two"); // Error: Argument of type 'string' is not assignable to 'number'
```

## Conditional Types

```typescript
// T extends U ? X : Y
type IsString<T> = T extends string ? true : false;

type A = IsString<"hello">;  // true
type B = IsString<42>;       // false

// Distributive conditional types
type ToArray<T> = T extends any ? T[] : never;
type Result = ToArray<string | number>;  // string[] | number[] (distributes)

// Non-distributive: wrap in tuple
type ToArrayNonDist<T> = [T] extends [any] ? T[] : never;
type Result2 = ToArrayNonDist<string | number>;  // (string | number)[]
```

## infer Keyword

`infer` declares a type variable within a conditional type to be inferred from a position.

```typescript
// Extract return type of a function
type MyReturnType<T> = T extends (...args: any[]) => infer R ? R : never;

type R1 = MyReturnType<() => string>;       // string
type R2 = MyReturnType<(x: number) => void>; // void

// Extract element type of an array
type ElementOf<T> = T extends (infer E)[] ? E : never;
type E1 = ElementOf<string[]>;  // string

// Extract first element of a tuple
type Head<T extends any[]> = T extends [infer First, ...any[]] ? First : never;
type H = Head<[1, "two", true]>;  // 1

// Extract parameters of a function
type MyParameters<T> = T extends (...args: infer P) => any ? P : never;
type P1 = MyParameters<(a: string, b: number) => void>;  // [a: string, b: number]
```

## Mapped Types

Transform each property in a type.

```typescript
// Make all properties optional
type MyPartial<T> = { [K in keyof T]?: T[K] };

// Make all properties readonly
type MyReadonly<T> = { readonly [K in keyof T]: T[K] };

// Transform value types
type Stringify<T> = { [K in keyof T]: string };

interface User { id: number; name: string; }
type StringUser = Stringify<User>;
// { id: string; name: string }

// Key remapping (TS 4.1+)
type Getters<T> = { [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K] };
type UserGetters = Getters<User>;
// { getId: () => number; getName: () => string }
```

## Template Literal Types

```typescript
type EventName = "click" | "focus" | "blur";
type HandlerName = `on${Capitalize<EventName>}`;
// "onClick" | "onFocus" | "onBlur"

type CSSValue = `${number}px` | `${number}%` | `${number}rem`;
const width: CSSValue = "100px";  // OK
const bad: CSSValue = "100em";    // Error
```

## Real-World Example: Typed API Client

```typescript
type ApiRoutes = {
  "/users": { get: User[]; post: User };
  "/users/:id": { get: User; put: User; delete: void };
  "/posts": { get: Post[] };
};

type ExtractParams<T extends string> =
  T extends `${string}:${infer Param}/${infer Rest}`
    ? { [K in Param | keyof ExtractParams<Rest>]: string }
    : T extends `${string}:${infer Param}`
      ? { [K in Param]: string }
      : {};

async function api<T extends keyof ApiRoutes>(
  path: T,
  method: keyof ApiRoutes[T],
  body?: any,
): Promise<any> {
  const res = await fetch(path, { method: method.toUpperCase(), body: body ? JSON.stringify(body) : undefined });
  return res.json();
}
```

## Common Bugs

- **Circular generic constraints**: `type A<T extends A<T>>` causes TypeScript to error or behave unexpectedly. Break circularity with intermediary types.
- **Excessive complexity**: Deeply nested generics (`Promise<Map<string, Set<number>>>`) cause slow type-checking. Extract intermediate types with aliases.
- **Generic defaults**: `interface Config<T = any>` defaults to `any`, silently losing type safety. Prefer explicit defaults or constraint-based defaults.
- **`T extends unknown` vs bare `T`**: `T extends unknown` distributes over unions; bare `T` does not. Choose intentionally.
- **Forgetting generic inference context**: TypeScript can't always infer generic types from usage—provide explicit types when inference fails: `identity<string>("hello")`.

## Time/Space

- Generic type checking adds to compile time. Complex conditional types can increase checking from milliseconds to seconds per file.
- At runtime, generics are erased—there is zero runtime overhead.
- `infer` types are resolved at compile time and have no runtime cost.
- Deeply recursive conditional types (e.g., recursive tuple manipulation) may hit TypeScript's recursion limit (~50 levels).
