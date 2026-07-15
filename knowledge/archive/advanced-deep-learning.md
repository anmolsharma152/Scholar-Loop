---
topic: ml-ai
difficulty: hard
tags: [ml, deep-learning, techniques]
---

# Advanced Deep Learning Techniques

## 1. Normalization Techniques

### Batch Normalization (BatchNorm)
- Normalizes across the **batch dimension** for each feature:
```
BN(x_i) = γ · (x_i - μ_B) / sqrt(σ²_B + ε) + β
```
- μ_B, σ²_B computed per mini-batch; γ, β are learnable scale/shift.
- **Pros**: Accelerates training, allows higher learning rates, mild regularization.
- **Cons**: Batch-size dependent (poor with small batches), breaks for variable-length sequences.

### Layer Normalization (LayerNorm)
- Normalizes across the **feature dimension** for each sample:
```
LN(x) = γ · (x - μ) / sqrt(σ² + ε) + β,  μ,σ computed over features
```
- **Batch-size independent** → standard in Transformers, RNNs.
- Used in all modern LLMs (GPT, BERT, LLaMA).

### Group Normalization (GroupNorm)
- Splits channels into groups; normalizes within each group per sample.
- **Batch-size independent** like LayerNorm; works well in computer vision.
- Good when batch size is very small (e.g., detection, video).

### Other Norms
- **RMSNorm**: Like LayerNorm but only scales (no centering): `RMSNorm(x) = x / RMS(x) · γ`. Faster; used in LLaMA.
- **Instance Norm**: Normalize per channel per sample (style transfer).

---

## 2. Attention Variants

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
- Keys and values shared across groups of query heads (e.g., 8 query heads share 1 KV pair).
- Reduces KV-cache size by factor of g (number of groups).
- Used in LLaMA-2, Mistral, Gemma.

### Multi-Query Attention (MQA)
- Extreme case of GQA: all query heads share a single KV pair.
- Maximum KV-cache reduction; slight quality loss.

### FlashAttention
- Not a new attention mechanism — an IO-aware algorithm.
- Fuses softmax, matrix multiply, and dropout into one kernel.
- Keeps intermediate results in GPU SRAM (not HBM) → 2-4x speedup, exact same output.

### Linear Attention / Sub-Quadratic
- Approximate softmax with kernel functions: `softmax(QK^T) ≈ φ(Q)φ(K)^T`.
- O(n·d²) instead of O(n²·d).
- Mamba/SSMs achieve similar via state-space formulation.

---

## 3. Residual Connections

```
y = x + F(x)
```
- Enables training of very deep networks (100+ layers) by providing gradient highways.
- Original residual: `H(x) = F(x) + x` — network learns the residual F(x) = H(x) - x.
- **Pre-norm** (modern): LayerNorm → Attention → Residual (smoother gradients).
- **Post-norm** (original): Attention → LayerNorm → Residual (original Transformer; less stable).
- **Why it works**: Gradients flow through the identity shortcut, avoiding vanishing gradients.

---

## 4. Learning Rate Schedules

### Warmup
- Linearly increase LR from ~0 to target over first `W` steps.
- Critical for Transformer training — gradients are unstable early on.
- Typical: warmup for 2000-10000 steps.

### Cosine Annealing
```
η_t = η_min + 0.5(η_max - η_min)(1 + cos(πt/T))
```
- Smoothly decays LR from max to near-zero over T steps.
- Standard for LLM training (GPT, LLaMA).

### Other Schedules
- **Step decay**: Multiply LR by 0.1 every N epochs.
- **Linear decay**: Linearly reduce to zero.
- **One-cycle policy**: Warmup then cosine decay (fast training).

---

## 5. Regularization Techniques

### Weight Decay (AdamW)
- Decoupled weight decay (not L2 regularization in Adam):
```
θ_{t+1} = (1 - λ) θ_t - η · m̂_t / (√v̂_t + ε)
```
- λ typically 0.01-0.1 for Transformers.
- AdamW (decoupled) is superior to standard Adam + L2 for Transformers.

### Label Smoothing
- Replace hard labels (0/1) with soft labels (ε/K, 1-ε+ε/K):
```
y_smooth = (1 - ε) · y_hard + ε / K
```
- ε = 0.1 is standard. Prevents overconfident predictions, improves calibration.

### Dropout
- Randomly zero out activations with probability p during training.
- **Attention dropout**: Applied to attention weights.
- **Hidden dropout**: Applied to output of layers.
- Modern LLMs often use low or zero dropout (rely on large data + weight decay).

### Mixup
- Interpolate between pairs of training examples:
```
x_mixed = λ x_i + (1-λ) x_j
y_mixed = λ y_i + (1-λ) y_j
```
- λ ~ Beta(α, α), α ∈ [0.2, 0.4].
- Improves generalization, robustness to adversarial examples.

### CutMix
- Cut a patch from one image and paste onto another; labels mixed proportionally to area.

---

## 6. Knowledge Distillation

- Train a smaller **student** model to mimic a larger **teacher** model.
- **Soft labels**: Student learns from teacher's softmax output (with temperature T > 1):
```
L = α · CE(y_hard, p_student) + (1-α) · KL(p_teacher^T || p_student^T)
```
Where `p^T = softmax(z/T)` (softened logits).
- **Why soft labels help**: They encode inter-class similarities (e.g., "3" is more similar to "8" than to "1").
- Used for: compressing LLMs, efficient edge deployment.

---

## 7. Neural Architecture Search (NAS)

### Search Space
- Define candidate operations per cell (convolutions, attention, skip connections).
- Define cell topology (how operations connect).

### Search Strategy
- **Reinforcement learning**: Controller network samples architectures; accuracy is reward.
- **Differentiable (DARTS)**: Make architecture choices continuous via softmax over operations; optimize jointly with weights.
- **Evolutionary**: Mutate and select top-performing architectures.

### Efficiency Constraints
- Multi-objective NAS: optimize accuracy AND latency/FLOPs.
- Hardware-aware NAS: search constrained to specific device (mobile GPU, TPU).

### Notable Results
- EfficientNet (compound scaling + NAS): State-of-the-art accuracy per FLOP.
- Once-for-All (OFA): Train one supernet, extract many sub-networks for different devices.

---

## 8. Positional Encodings

### Sinusoidal (Original Transformer)
```
PE(pos, 2i)   = sin(pos / 10000^(2i/d))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d))
```
- Fixed; generalizes to unseen lengths.

### Learned Positional Embeddings
- Train a separate embedding for each position. GPT-2, BERT.
- Limited to max training length.

### RoPE (Rotary Position Embeddings)
- Encode position by rotating query/key vectors in 2D subspaces:
```
q_m = R_θ_m · q,   k_n = R_θ_n · k
```
- Dot product `q_m · k_n` depends on relative position (m-n).
- Used in LLaMA, Mistral, Qwen — enables longer context via NTK-aware scaling.

### ALiBi (Attention with Linear Biases)
- Add linear bias to attention scores based on distance: `score += m · |i-j|`.
- No learned positional embeddings; simple, effective for extrapolation.

---

## 9. Mixed Precision Training

- Forward pass in FP16/BF16 (faster, less memory).
- Master weights in FP32 for stable updates.
- **Loss scaling**: Multiply loss by large constant to prevent underflow in FP16 gradients.
- **BF16**: Wider exponent range than FP16 — more stable, preferred on modern GPUs (A100, H100).

---

## 10. Key Hyperparameter Ranges for Transformers

| Parameter | Typical Range |
|---|---|
| Learning rate | 1e-4 to 3e-4 (LLMs), 1e-3 (smaller models) |
| Warmup steps | 2000–10000 |
| Weight decay | 0.01–0.1 |
| Dropout | 0.0–0.1 |
| Label smoothing | 0.0–0.1 |
| Batch size | 32–4096 (tokens: 32k–1M) |
| β₁, β₂ (Adam) | 0.9, 0.95–0.999 |
| ε (Adam) | 1e-8 |
| Gradient clip | 1.0 |
