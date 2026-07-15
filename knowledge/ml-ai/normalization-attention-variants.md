---
topic: ml-ai
difficulty: hard
tags: [ml, deep-learning, normalization, attention]
---

# Normalization & Attention Variants

## Normalization Techniques

### Batch Normalization (BatchNorm)
- Normalizes across the **batch dimension** for each feature:
```
BN(x_i) = γ · (x_i - μ_B) / sqrt(σ²_B + ε) + β
```
- μ_B, σ²_B computed per mini-batch; γ, β are learnable scale/shift
- **Pros**: Accelerates training, allows higher learning rates, mild regularization
- **Cons**: Batch-size dependent (poor with small batches), breaks for variable-length sequences

### Layer Normalization (LayerNorm)
- Normalizes across the **feature dimension** for each sample:
```
LN(x) = γ · (x - μ) / sqrt(σ² + ε) + β,  μ,σ computed over features
```
- **Batch-size independent** → standard in Transformers, RNNs
- Used in all modern LLMs (GPT, BERT, LLaMA)

### Group Normalization (GroupNorm)
- Splits channels into groups; normalizes within each group per sample
- **Batch-size independent** like LayerNorm; works well in computer vision
- Good when batch size is very small (e.g., detection, video)

### Other Norms
- **RMSNorm**: Like LayerNorm but only scales (no centering): `RMSNorm(x) = x / RMS(x) · γ`. Faster; used in LLaMA
- **Instance Norm**: Normalize per channel per sample (style transfer)

## Attention Variants

### Standard Self-Attention
```
Attn(Q, K, V) = softmax(QK^T / √d_k) V
```
O(n²) in sequence length n.

### Multi-Head Attention
- h parallel attention heads with independent projections, concatenated:
```
MultiHead(Q,K,V) = Concat(head_1, ..., head_h) W^O
head_i = Attn(QW_i^Q, KW_i^K, VW_i^V)
```

### Grouped-Query Attention (GQA)
- Keys and values shared across groups of query heads (e.g., 8 query heads share 1 KV pair)
- Reduces KV-cache size by factor of g (number of groups)
- Used in LLaMA-2, Mistral, Gemma

### Multi-Query Attention (MQA)
- Extreme case of GQA: all query heads share a single KV pair
- Maximum KV-cache reduction; slight quality loss

### FlashAttention
- Not a new attention mechanism — an IO-aware algorithm
- Fuses softmax, matrix multiply, and dropout into one kernel
- Keeps intermediate results in GPU SRAM (not HBM) → 2-4x speedup, exact same output

### Linear Attention / Sub-Quadratic
- Approximate softmax with kernel functions: `softmax(QK^T) ≈ φ(Q)φ(K)^T`
- O(n·d²) instead of O(n²·d)
- Mamba/SSMs achieve similar via state-space formulation

## Residual Connections

```
y = x + F(x)
```
- Enables training of very deep networks (100+ layers) by providing gradient highways
- **Pre-norm** (modern): LayerNorm → Attention → Residual (smoother gradients)
- **Post-norm** (original): Attention → LayerNorm → Residual (original Transformer; less stable)
- **Why it works**: Gradients flow through the identity shortcut, avoiding vanishing gradients
