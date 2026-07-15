---
topic: fullstack
difficulty: medium
tags: [typescript, generics, advanced-types]
last_sent:
review_count: 0
---

# TypeScript Generics: Basics

Generics let you write reusable components that work with any type while maintaining type safety.

Generic functions use type parameters (conventionally `<T>`) to capture the caller-provided type:

```typescript
function identity<T>(arg: T): T {
  return arg;
}
```

**Multiple type parameters:** `<T, U>` for functions that work with multiple types. Use extends for constraints: `<T extends HasLength>` ensures T has a `.length` property. Constraints can use keyof: `getProperty<T, K extends keyof T>(obj: T, key: K): T[K]`.

**Generic functions vs. any:** Generics preserve type information (`identity<string>("hi")` returns `string`). `any` loses all type safety.

## Generic Constraints

```typescript
interface HasLength { length: number; }
function logLength<T extends HasLength>(arg: T): T {
  console.log(arg.length);
  return arg;
}
```

**Using keyof with generics:**
```typescript
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}
```

**Conditional types** enable type-level programming:
```typescript
type IsString<T> = T extends string ? true : false;
type A = IsString<"hello">;  // true
type B = IsString<42>;       // false
```

**Infer keyword** extracts types from inside other types:
```typescript
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : never;
type ElementType<T> = T extends (infer U)[] ? U : never;
```

## Generic Interfaces & Types

```typescript
interface ApiResponse<T> {
  data: T;
  status: number;
  error?: string;
}
```

## Key Difference: Type vs Interface

- Both can define generic shapes
- `interface` can be extended/merged; `type` cannot be merged (uses intersection `&`)
- `type` works with union types and conditional types
- Prefer `interface` for public APIs; `type` when you need computed properties or unions
