---
difficulty: easy
last_sent: 2026-07-15 04:31:28.240024+00:00
review_count: 1
tags:
- typescript
topic: fullstack
---

# TypeScript Basics

TypeScript adds a static type system to JavaScript. It catches type errors at compile time, improves IDE tooling, and documents intent—all while being fully interoperable with existing JS code.

## Primitive and Literal Types

```typescript
let name: string = "Alice";
let age: number = 30;
let active: boolean = true;
let data: null = null;
let nothing: undefined = undefined;

// Literal types: restrict to specific values
let status: "idle" | "loading" | "error" = "idle";
let count: 0 | 1 | 2 = 1;
```

## Interfaces and Type Aliases

```typescript
// Interface: extendable, merges with other interfaces
interface User {
  id: number;
  name: string;
  email: string;
  createdAt?: Date;  // optional
}

interface Admin extends User {
  role: "admin" | "superadmin";
}

// Type alias: more flexible, supports unions and mapped types
type ID = string | number;

type ApiResponse<T> = {
  data: T;
  status: number;
  error?: string;
};
```

**When to use which**: Use `interface` for object shapes that may be extended. Use `type` for unions, intersections, mapped types, and primitives.

## Enums

```typescript
// Numeric enum (auto-incrementing)
enum Direction {
  Up,     // 0
  Down,   // 1
  Left,   // 2
  Right,  // 3
}

// String enum (explicit values)
enum Status {
  Active = "ACTIVE",
  Inactive = "INACTIVE",
}

// Const enum: inlined at compile time (no runtime object)
const enum Color {
  Red = "RED",
  Green = "GREEN",
}
```

## Utility Types

```typescript
interface User {
  id: number;
  name: string;
  email: string;
  role: string;
}

// Partial: all properties optional
type UserUpdate = Partial<User>;
// { id?: number; name?: string; email?: string; role?: string }

// Required: all properties required
type FullUser = Required<User>;

// Pick: select specific properties
type UserPreview = Pick<User, "id" | "name">;
// { id: number; name: string }

// Omit: exclude specific properties
type CreateUser = Omit<User, "id">;
// { name: string; email: string; role: string }

// Record: construct an object type with specific key/value types
type Roles = Record<string, string[]>;
// { admin: string[]; user: string[]; ... }

// Readonly
type FrozenUser = Readonly<User>;

// ReturnType: extract the return type of a function
function getUser() { return { id: 1, name: "Alice" }; }
type UserType = ReturnType<typeof getUser>;
// { id: number; name: string }

// Parameters: extract function parameter types
type GetUserParams = Parameters<typeof getUser>;
// []
```

## Type Assertions and Narrowing

```typescript
// Type assertion (override inference)
const input = document.getElementById("name") as HTMLInputElement;
input.value = "Alice";

// Type guard with typeof
function format(value: string | number): string {
  if (typeof value === "string") {
    return value.toUpperCase();  // narrowed to string
  }
  return value.toFixed(2);       // narrowed to number
}

// Type guard with in
interface Bird { fly(): void; }
interface Fish { swim(): void; }

function move(animal: Bird | Fish) {
  if ("fly" in animal) {
    animal.fly();
  } else {
    animal.swim();
  }
}

// Exhaustive check
function handle(status: "ok" | "error") {
  switch (status) {
    case "ok": return "success";
    case "error": return "failure";
    default: const _: never = status; return _;
  }
}
```

## Arrays and Tuples

```typescript
let numbers: number[] = [1, 2, 3];
let names: Array<string> = ["Alice", "Bob"];

// Tuple: fixed-length array with specific types
let pair: [string, number] = ["Alice", 30];
let [first, second] = pair;  // first: string, second: number

// Readonly tuple
type Point = readonly [number, number];
```

## Functions

```typescript
function add(a: number, b: number): number {
  return a + b;
}

// Optional and default parameters
function greet(name: string, greeting: string = "Hello"): string {
  return `${greeting}, ${name}!`;
}

// Rest parameters
function sum(...nums: number[]): number {
  return nums.reduce((a, b) => a + b, 0);
}

// Function overload
function pad(input: string): string;
function pad(input: number): string;
function pad(input: string | number): string {
  return typeof input === "string" ? input.padStart(10) : String(input).padStart(10);
}
```

## Common Bugs

- **`any` type escape hatch**: Using `any` disables type checking. Prefer `unknown` and narrow with type guards.
- **Implicit `undefined`**: Forgetting that optional properties may be `undefined`. Use `!` operator only when you're certain, or check explicitly.
- **Interface vs type in error messages**: TypeScript error messages show the alias name for `type` but expand interfaces—use `type` when you want readable error names.
- **Const assertions**: Without `as const`, object literal properties widen to their base types. Use `as const` for literal tuples and readonly values.
- **Enum pitfalls**: Numeric enums are reverse-mapped (you can do `Direction[0]` which returns `"Up"`). This can cause unexpected behavior. Prefer string enums or union types.