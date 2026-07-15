---
topic: ml-ai
difficulty: hard
tags: [ml, deep-learning, training, regularization]
---

# Training & Regularization Techniques

## Learning Rate Schedules

### Warmup
- Linearly increase LR from ~0 to target over first `W` steps
- Critical for Transformer training — gradients are unstable early on
- Typical: warmup for 2000-10000 steps

### Cosine Annealing
```
η_t = η_min + 0.5(η_max - η_min)(1 + cos(πt/T))
```
- Smoothly decays LR from max to near-zero over T steps
- Standard for LLM training (GPT, LLaMA)

### Other Schedules
- **Step decay**: Multiply LR by 0.1 every N epochs
- **Linear decay**: Linearly reduce to zero
- **One-cycle policy**: Warmup then cosine decay (fast training)

## Regularization Techniques

### Weight Decay (AdamW)
- Decoupled weight decay (not L2 regularization in Adam):
```
θ_{t+1} = (1 - λ) θ_t - η · m̂_t / (√v̂_t + ε)
```
- λ typically 0.01-0.1 for Transformers
- AdamW (decoupled) is superior to standard Adam + L2 for Transformers

### Label Smoothing
- Replace hard labels (0/1) with soft labels (ε/K, 1-ε+ε/K):
```
y_smooth = (1 - ε) · y_hard + ε / K
```
- ε = 0.1 is standard. Prevents overconfident predictions, improves calibration

### Dropout
- Randomly zero out activations with probability p during training
- **Attention dropout**: Applied to attention weights
- **Hidden dropout**: Applied to output of layers
- Modern LLMs often use low or zero dropout (rely on large data + weight decay)

### Mixup
- Interpolate between pairs of training examples:
```
x_mixed = λ x_i + (1-λ) x_j
y_mixed = λ y_i + (1-λ) y_j
```
- λ ~ Beta(α, α), α ∈ [0.2, 0.4]
- Improves generalization, robustness to adversarial examples

### CutMix
- Cut a patch from one image and paste onto another; labels mixed proportionally to area

## Knowledge Distillation

- Train a smaller **student** model to mimic a larger **teacher** model
- **Soft labels**: Student learns from teacher's softmax output (with temperature T > 1):
```
L = α · CE(y_hard, p_student) + (1-α) · KL(p_teacher^T || p_student^T)
```
- **Why soft labels help**: They encode inter-class similarities (e.g., "3" is more similar to "8" than to "1")
- Used for: compressing LLMs, efficient edge deployment

## Neural Architecture Search (NAS)

### Search Strategy
- **Reinforcement learning**: Controller network samples architectures; accuracy is reward
- **Differentiable (DARTS)**: Make architecture choices continuous via softmax over operations
- **Evolutionary**: Mutate and select top-performing architectures

### Notable Results
- **EfficientNet** (compound scaling + NAS): State-of-the-art accuracy per FLOP
- **Once-for-All (OFA)**: Train one supernet, extract many sub-networks for different devices

## Positional Encodings

### Sinusoidal (Original Transformer)
```
PE(pos, 2i)   = sin(pos / 10000^(2i/d))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d))
```
- Fixed; generalizes to unseen lengths

### RoPE (Rotary Position Embeddings)
- Encode position by rotating query/key vectors in 2D subspaces
- Dot product `q_m · k_n` depends on relative position (m-n)
- Used in LLaMA, Mistral, Qwen — enables longer context via NTK-aware scaling

### ALiBi (Attention with Linear Biases)
- Add linear bias to attention scores based on distance: `score += m · |i-j|`
- No learned positional embeddings; simple, effective for extrapolation

## Mixed Precision Training

- Forward pass in FP16/BF16 (faster, less memory)
- Master weights in FP32 for stable updates
- **Loss scaling**: Multiply loss by large constant to prevent underflow in FP16 gradients
- **BF16**: Wider exponent range than FP16 — more stable, preferred on modern GPUs (A100, H100)
