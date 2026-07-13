---
topic: ml-ai
difficulty: hard
tags: [ml, mamba, ssm, efficient]
---

# State Space Models & Mamba

## 1. State Space Model (SSM) Formulation

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

---

## 2. S4: Structured State Spaces for Sequences

**Key Innovation**: Initialize A using **HiPPO** (High-order Polynomial Projection Operator) framework.

### HiPPO Initialization
- A is initialized as a specific matrix that enables optimal online compression of the input signal's history.
- A_{nk} = -((2n+1)^{1/2} (2k+1)^{1/2}) · { if n > k: 1, else: 0 }
- This prevents the "forgetting" problem that plagues naive SSM initializations.

### Computation Modes
1. **Convolution mode**: Compute global convolution kernel K = (C B̄, C Ā B̄, C Ā² B̄, ...) and apply as 1D convolution. Parallel, O(n log n) with FFT.
2. **Recurrence mode**: Compute step-by-step x_k = Ā x_{k-1} + B̄ u_k. Sequential, O(n). Best for autoregressive generation.

### Limitations of S4
- **A, B, C are fixed** (not input-dependent) → cannot perform content-based reasoning.
- Behaves like a linear time-invariant (LTI) system — same filter applied everywhere.
- Good for long-range dependencies in fixed-pattern data (e.g., long-range audio, ECG), but weak on tasks requiring selective attention.

---

## 3. Mamba: Selective State Spaces

**Core Insight** (Gu & Dao, 2023): Make the SSM parameters **input-dependent** (selective).

### Selective Scan
Instead of fixed B, C, Δ:
```
B_k = Linear(u_k)        (input-dependent)
C_k = Linear(u_k)        (input-dependent)
Δ_k = softplus(Linear(u_k))  (input-dependent, controls "memory length")
```

At each step k:
```
x_k = Ā_k x_{k-1} + B̄_k u_k
y_k = C_k x_k
```

Where:
```
Ā_k = exp(Δ_k A)
B̄_k = Δ_k B_k
```

**Why Δ matters**:
- Large Δ_k → Ā_k ≈ 0 → "forget" past state, reset → acts like a **not-gating** mechanism.
- Small Δ_k → Ā_k ≈ I → pass through, ignore input → acts like an **ignore** mechanism.
- The model learns to selectively remember or forget based on content.

### Parallel Associative Scan (Hardware-Efficient Implementation)
Naive sequential scan is O(n) but not parallelizable on GPU.

**Key insight**: The recurrence `x_k = A_k x_{k-1} + B_k` is an **associative scan** problem:
```
(a ⊕ b) ⊕ c = a ⊕ (b ⊕ c)
```

Mamba uses the parallel associative scan algorithm:
- Compute prefix sums of (A, B) pairs in log(n) parallel steps.
- Map onto GPU using custom CUDA kernels.
- Same asymptotic cost as parallel attention: O(n · d · L) but with much smaller constants.

### Hardware Considerations
- No need to materialize the full n×n attention matrix → O(n) memory.
- Custom CUDA kernel avoids HBM reads/writes — keeps state in SRAM.
- Recurrent mode: O(1) memory per step during generation (no KV-cache).

---

## 4. Mamba Block Architecture

```
Input x
  ├── Linear → SiLU → Conv1d → SiLU → (B, C, Δ projected here)
  │                        │
  │                   Selective SSM
  │                        │
  └── Linear (gate) ──→ × (multiply) ──→ Output
```

- **Gating**: Multiplicative gating (like SwiGLU in Transformers).
- **Conv1d**: Local convolution before the SSM provides local context.
- **Selective parameters**: B, C, Δ computed from input via linear projections + softplus.

---

## 5. Mamba-2: Connections to Attention

Recent work (Dao & Gu, 2024) showed SSMs can be cast as a form of **structured attention**:

```
SSM output = diag(C) · (I - diag(Ā))⁻¹ · diag(B) · U
```

This is equivalent to a linear attention with specific masking structure:
- **Input-dependent**: B, C act like keys and values.
- **State matrix A**: Controls decay/forgetting.
- Mamba-2 achieves 2-8x speedup over Mamba-1 via tensor parallelism improvements.

---

## 6. Transformers vs. Mamba/SSM: Detailed Comparison

| Property | Transformer | Mamba (SSM) |
|---|---|---|
| **Complexity** | O(n² · d) | O(n · d · N) |
| **Memory** | O(n²) or O(n·d) KV-cache | O(n · d) — no KV-cache |
| **Parallelism** | Fully parallel (training) | Parallel associative scan |
| **Recurrence** | N/A (autoregressive via KV-cache) | O(1) per step (natural RNN) |
| **Long sequences** | Limited by context window | Excellent — linear scaling |
| **Retrieval/copying** | Excellent (attention can copy exactly) | Weaker — smoothed state |
| **In-context learning** | Strong (attention is flexible) | Weaker (state is compressed) |
| **Training** | Mature (FlashAttention, etc.) | Custom CUDA kernels needed |
| **Generation** | O(1) per token (KV-cache lookup) | O(1) per token (recurrent state) |

### When to Choose Mamba
- **Long sequences**: Genomics, audio, time-series where n >> 10k tokens.
- **Low-latency inference**: Recurrent mode avoids KV-cache overhead.
- **Resource-constrained**: O(n) memory is critical (edge devices, mobile).
- **Streaming**: Natural fit for real-time continuous data.

### When to Choose Transformers
- **Exact retrieval**: Copying, lookup tasks require attention's direct access to all tokens.
- **In-context learning**: Few-shot prompting benefits from attention's flexibility.
- **Mature ecosystem**: Better tooling, libraries, optimized kernels.
- **Short to moderate sequences**: n < 10k — quadratic cost is manageable.

---

## 7. Hybrid Architectures

Most practical systems combine both:

- **Jamba** (AI21): Alternates Transformer layers and Mamba layers. Gets benefits of both attention and linear scaling.
- **Zamba**: Similar hybrid with shared Transformer layers across Mamba blocks.
- **Griffin** (Google): Gated linear recurrence + local attention.

### Hybrid Design Patterns
```
[Mamba Block] × L₁ → [Attention Block] × L₂ → [Mamba Block] × L₁ → ...
```
- Mamba layers handle bulk of sequence processing cheaply.
- Attention layers handle tasks requiring global retrieval.

---

## 8. Key Equations Summary

```
Continuous SSM:   x'(t) = A x(t) + B u(t),  y(t) = C x(t)
Discretized:      x_k = Ā x_{k-1} + B̄ u_k,  y_k = C x_k
HiPPO-A:          A_{nk} = -(2n+1)^{1/2} (2k+1)^{1/2} · [n > k]
Selective:        B_k, C_k, Δ_k = f(u_k)     (input-dependent)
Convolution kernel: K = [C B̄, C Ā B̄, C Ā² B̄, ..., C Ā^{L-1} B̄]
Parallel scan:    associative operator (A_k, B_k) ⊕ (A_{k+1}, B_{k+1})
```

---

## 9. Open Challenges

- **Scaling to very large models**: Mamba demonstrated at 1.3B–2.8B; unclear if competitive at 70B+ scale.
- **Multimodal**: How to extend selective SSM to vision, audio, and cross-modal tasks.
- **Training efficiency**: Custom kernels are less mature than FlashAttention.
- **Benchmarking**: Mamba excels on synthetic recall tasks; real-world evaluation on diverse NLP benchmarks still evolving.
- **Combining with attention**: Optimal hybrid architectures and layer ratios remain an active research area.
