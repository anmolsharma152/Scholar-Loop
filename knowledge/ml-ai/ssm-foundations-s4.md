---
topic: ml-ai
difficulty: hard
tags: [ml, ssm, s4, hipo]
---

# State Space Models: Foundations & S4

## State Space Model (SSM) Formulation

SSMs are inspired by continuous-time linear systems from control theory:

```
dx/dt = A x(t) + B u(t)     (state equation)
y(t)  = C x(t) + D u(t)     (output equation)
```

| Symbol | Shape | Role |
|---|---|---|
| x(t) | (N, 1) | Latent state vector, dimension N |
| u(t) | (1, 1) | Input (scalar for each feature) |
| y(t) | (1, 1) | Output |
| A | (N, N) | State transition matrix |
| B | (N, 1) | Input-to-state projection |
| C | (1, N) | State-to-output projection |
| D | (1, 1) | Skip connection (often set to 0) |

### Discretization
To apply to discrete sequences, discretize with step size Δ:
```
Ā = exp(Δ A)
B̄ = (Δ A)⁻¹ (Ā - I) · Δ B    (zero-order hold)
```

Discrete recurrence:
```
x_k = Ā x_{k-1} + B̄ u_k
y_k = C x_k + D u_k
```

This is a **linear recurrence** — can be computed as a convolution or a recurrence.

## S4: Structured State Spaces for Sequences

**Key Innovation**: Initialize A using **HiPPO** (High-order Polynomial Projection Operator) framework.

### HiPPO Initialization
- A is initialized as a specific matrix that enables optimal online compression of the input signal's history
- A_{nk} = -((2n+1)^{1/2} (2k+1)^{1/2}) · { if n > k: 1, else: 0 }
- This prevents the "forgetting" problem that plagues naive SSM initializations

### Computation Modes
1. **Convolution mode**: Compute global convolution kernel K = (C B̄, C Ā B̄, C Ā² B̄, ...) and apply as 1D convolution. Parallel, O(n log n) with FFT
2. **Recurrence mode**: Compute step-by-step x_k = Ā x_{k-1} + B̄ u_k. Sequential, O(n). Best for autoregressive generation

### Limitations of S4
- **A, B, C are fixed** (not input-dependent) → cannot perform content-based reasoning
- Behaves like a linear time-invariant (LTI) system — same filter applied everywhere
- Good for long-range dependencies in fixed-pattern data (e.g., long-range audio, ECG), but weak on tasks requiring selective attention
