---
difficulty: medium
last_sent:
review_count: 0
tags:
  - math
  - calculus
topic: dsa
---

# Calculus: Functions, Partial Derivatives & Gradients

Source: Masai_X_IITMandi Trimester 1 — Dr. Indu Joshi, IIT Mandi

---

## 1. Functions

A function f: X -> Y associates each element of X (domain) to exactly one element of Y (codomain).

**Range**: f(X) = {f(x) : x in X} is subset of codomain. Range is actual outputs; codomain is potential outputs.

### Key Function Types

| Type | Definition | Example |
|------|-----------|---------|
| Constant | f(x) = c for all x | f(x) = 5 |
| Identity | f(x) = x | f(x) = x |
| Even | f(-x) = f(x) | f(x) = x^2 |
| Odd | f(-x) = -f(x) | f(x) = x^3, sin(x) |
| Exponential | f(x) = a^x, a > 0 | f(x) = e^x |
| Logarithmic | f(x) = log_a(x), x > 0 | f(x) = ln(x) |
| Modulus | f(x) = |x| | f(x) = |x| |
| Greatest Integer | f(x) = [x] | f(2.7) = 2 |

### Function Classifications

- **One-to-One (Injection)**: x != y => f(x) != f(y). Each input maps to unique output.
- **Onto (Surjection)**: Range = Codomain. Every output has at least one pre-image.
- **Bijection**: One-to-one AND onto. Invertible.
- **Many-to-One**: Multiple inputs map to same output (e.g., f(x) = x^2)

### Inverse Function
If f is a bijection, f^(-1): Y -> X exists such that f(f^(-1)(y)) = y.

Example: f(x) = x/(x+1) on R\{-1} -> R\{1}
f^(-1)(y) = y/(1-y)

---

## 2. Functions of Several Variables

For f: R^n -> R, the function maps n-dimensional input to scalar output.

    y = f(x1, x2, ..., xn)

**Domain**: D(f) = {(x1,...,xn) in R^n | f is defined}
**Range**: R(f) = {f(x1,...,xn) | (x1,...,xn) in D(f)}

### Examples
- f(x,y) = x^2 + y^2: Domain = R^2, Range = [0, inf)
- f(x,y) = sqrt(y - x^2): Domain = {(x,y) : y >= x^2}, Range = [0, inf)
- f(x,y) = x/(x+1): Domain = R^2 \ {x = -1}

---

## 3. Partial Derivatives

For f: R^n -> R, the partial derivative with respect to xi measures rate of change when only xi varies (all other variables held constant).

### First-Order Partial Derivatives

    fx_i = df/dx_i = lim_{h->0} [f(x1,..,xi+h,..,xn) - f(x1,..,xi,..,xn)] / h

For f: R^2 -> R:
- fx = df/dx (differentiate w.r.t. x, treat y as constant)
- fy = df/dy (differentiate w.r.t. y, treat x as constant)

### Second-Order Partial Derivatives

    fxx = d^2f/dx^2 = d(fx)/dx
    fyy = d^2f/dy^2 = d(fy)/dy
    fxy = d^2f/(dy*dx) = d(fx)/dy (mixed partial)

**Clairaut's Theorem**: If fxy and fyx are continuous, then fxy = fyx.

### Worked Example
f(x,y) = x^4 - x^2*y^2 + y^4 at (-1, 1):

- fx = 4x^3 - 2xy^2 => fx(-1,1) = -4 + 2 = -2
- fy = -2x^2*y + 4y^3 => fy(-1,1) = -2 + 4 = 2
- fxx = 12x^2 - 2y^2 => fxx(-1,1) = 12 - 2 = 10
- fyy = -2x^2 + 12y^2 => fyy(-1,1) = -2 + 12 = 10
- fxy = -4xy => fxy(-1,1) = 4

---

## 4. Gradient

The **gradient** generalizes the derivative to scalar functions of several variables.

For f: R^n -> R:

    nabla(f) = [df/dx1, df/dx2, ..., df/dx_n]^T

It's a vector pointing in the direction of steepest ascent.

### Properties
- nabla(f) points in direction of maximum rate of increase
- |nabla(f)| = magnitude of steepest ascent
- nabla(f) is perpendicular to level sets (contour lines)

### Example
f(x,y,z) = x^3 - 3xy^2 + x^2*y + y^3 + zy at (-1, 0, 1):

- fx = 3x^2 - 3y^2 + 2xy => fx(-1,0,1) = 3
- fy = -6xy + x^2 + 3y^2 + z => fy(-1,0,1) = 1 + 1 = 2
- fz = y => fz(-1,0,1) = 0

    nabla(f)(-1,0,1) = [3, 2, 0]^T

---

## 5. Directional Derivatives

The **directional derivative** of f at point P in direction of unit vector u gives the rate of change of f in that direction.

    D_u f(P) = lim_{h->0} [f(P + h*u) - f(P)] / h

### Formula
    D_u f(P) = nabla(f)(P) · u = |nabla(f)(P)| * cos(theta)

where theta is angle between gradient and direction u.

### Key Insights
- **Maximum** increase: when u is parallel to nabla(f), theta = 0, D_u f = |nabla(f)|
- **Minimum** increase: when u is antiparallel to nabla(f), theta = pi, D_u f = -|nabla(f)|
- **No change**: when u is perpendicular to nabla(f), theta = pi/2, D_u f = 0

### Worked Example
f(x,y) = x^2 + y^2 at P(1,2) in direction v = [3,4]:

- nabla(f) = [2x, 2y] => nabla(f)(1,2) = [2, 4]
- |v| = sqrt(9+16) = 5, unit vector u = [3/5, 4/5]
- D_u f(P) = [2,4] · [3/5, 4/5] = 6/5 + 16/5 = 22/5

---

## 6. Applications in ML

| Concept | ML Application |
|---------|---------------|
| Partial derivatives | Computing gradients for backpropagation |
| Gradient | Gradient descent optimization |
| Directional derivative | Understanding loss landscape geometry |
| Gradient magnitude | Learning rate selection |
| Hessian (2nd partials) | Newton's method, curvature analysis |
| Chain rule | Backpropagation through layers |
