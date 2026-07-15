---
topic: ml-ai
difficulty: hard
tags: [ml, mamba, selective-ssm]
---

# Mamba: Selective State Spaces

## Core Insight

Mamba (Gu & Dao, 2023) makes SSM parameters **input-dependent** (selective), solving S4's inability to do content-based reasoning.

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

**Why Δ matters**:
- Large Δ_k → Ā_k ≈ 0 → "forget" past state, reset → acts like a **not-gating** mechanism
- Small Δ_k → Ā_k ≈ I → pass through, ignore input → acts like an **ignore** mechanism
- The model learns to selectively remember or forget based on content

### Parallel Associative Scan (Hardware-Efficient)
Naive sequential scan is O(n) but not parallelizable on GPU.

**Key insight**: The recurrence `x_k = A_k x_{k-1} + B_k` is an **associative scan** problem:
```
(a ⊕ b) ⊕ c = a ⊕ (b ⊕ c)
```

Mamba uses the parallel associative scan algorithm:
- Compute prefix sums of (A, B) pairs in log(n) parallel steps
- Map onto GPU using custom CUDA kernels
- Same asymptotic cost as parallel attention: O(n · d · L) but with much smaller constants

### Hardware Considerations
- No need to materialize the full n×n attention matrix → O(n) memory
- Custom CUDA kernel avoids HBM reads/writes — keeps state in SRAM
- Recurrent mode: O(1) memory per step during generation (no KV-cache)

## Mamba Block Architecture

```
Input x
  ├── Linear → SiLU → Conv1d → SiLU → (B, C, Δ projected here)
  │                        │
  │                   Selective SSM
  │                        │
  └── Linear (gate) ──→ × (multiply) ──→ Output
```

- **Gating**: Multiplicative gating (like SwiGLU in Transformers)
- **Conv1d**: Local convolution before the SSM provides local context
- **Selective parameters**: B, C, Δ computed from input via linear projections + softplus

## Mamba-2: Connections to Attention

Recent work (Dao & Gu, 2024) showed SSMs can be cast as a form of **structured attention**:

```
SSM output = diag(C) · (I - diag(Ā))⁻¹ · diag(B) · U
```

This is equivalent to a linear attention with specific masking structure:
- **Input-dependent**: B, C act like keys and values
- **State matrix A**: Controls decay/forgetting
- Mamba-2 achieves 2-8x speedup over Mamba-1 via tensor parallelism improvements

## Transformers vs. Mamba

| Property | Transformer | Mamba (SSM) |
|---|---|---|
| **Complexity** | O(n² · d) | O(n · d · N) |
| **Memory** | O(n²) or O(n·d) KV-cache | O(n · d) — no KV-cache |
| **Long sequences** | Limited by context window | Excellent — linear scaling |
| **Retrieval/copying** | Excellent (attention can copy exactly) | Weaker — smoothed state |
| **In-context learning** | Strong (attention is flexible) | Weaker (state is compressed) |

### When to Choose Mamba
- **Long sequences**: Genomics, audio, time-series where n >> 10k tokens
- **Low-latency inference**: Recurrent mode avoids KV-cache overhead
- **Streaming**: Natural fit for real-time continuous data

### When to Choose Transformers
- **Exact retrieval**: Copying, lookup tasks require attention's direct access to all tokens
- **In-context learning**: Few-shot prompting benefits from attention's flexibility
- **Short to moderate sequences**: n < 10k — quadratic cost is manageable

## Hybrid Architectures

Most practical systems combine both:
- **Jamba** (AI21): Alternates Transformer layers and Mamba layers
- **Zamba**: Similar hybrid with shared Transformer layers across Mamba blocks
- **Griffin** (Google): Gated linear recurrence + local attention
