---
topic: ml-ai
difficulty: hard
tags: [ml, architectures, transformers, mamba, diffusion]
---

# Modern AI Architectures

## 1. Transformers

**Core Mechanism**: Scaled dot-product attention over Query, Key, Value projections.

```
Attn(Q, K, V) = softmax(QK^T / sqrt(d_k)) V
```

- **Multi-Head Attention**: Run `h` parallel attention heads with independent projections, concatenate outputs.
- **Positional Encoding**: Transformers lack inherent sequence order — positional encodings (sinusoidal, learned, or RoPE) inject position information.
- **Complexity**: O(n² · d) for sequence length n — quadratic in context length.

**Variant: BERT (Encoder-Only)**
- Bidirectional; sees full context left and right.
- Pre-training: Masked Language Modeling (MLM) + Next Sentence Prediction.
- Best for classification, NER, similarity tasks.

**Variant: GPT (Decoder-Only)**
- Causal (unidirectional) attention mask — left-to-right generation.
- Pre-training: Next-Token Prediction (autoregressive).
- Scales to large language models (GPT-4, Claude, Gemini).
- In-context learning: no fine-tuning needed for many tasks.

**Variant: Vision Transformer (ViT)**
- Splits image into fixed-size patches, linearly projects each to an embedding, prepends a [CLS] token.
- Works like a sentence of patches — applies standard Transformer encoder.
- Needs large datasets or strong pre-training; CNNs still win on small data.

---

## 2. State Space Models (SSM) / Mamba

**Motivation**: Transformers have O(n²) attention — Mamba achieves O(n) linear scaling.

**SSM Formulation** (continuous):
```
x'(t) = A x(t) + B u(t)
y(t)  = C x(t) + D u(t)
```

Discretized via zero-order hold; A, B, C are state matrices learned per-layer.

**S4 (Structured State Spaces for Sequences)**: HiPPO-initialized matrices A enable long-range dependencies without quadratic attention.

**Mamba's Selective Scan**:
- Makes B, C, and Δ (discretization step) **input-dependent** (selective), not fixed.
- Allows content-aware reasoning — model decides what to remember or forget.
- Hardware-efficient parallel scan implementation (associative scan on GPU).
- Recurrent mode: O(1) per-step during inference — no KV-cache needed.

**Strengths**: Linear scaling, efficient long-sequence modeling, recurrent inference.
**Weaknesses**: Weaker on tasks requiring exact retrieval / copying (where quadratic attention excels).

---

## 3. Mixture of Experts (MoE)

- Sparse MoE layers replace dense FFN layers with `N` expert sub-networks.
- A **router/gating network** selects top-k experts per token (typically k=2).
- Total parameters large, but only a fraction activated per token → computational efficiency at scale.
- **Key tradeoff**: Load balancing across experts (avoid collapse), routing overhead, communication in distributed training.
- Used in Mixtral, Switch Transformer, GPT-4 (rumored).

---

## 4. Diffusion Models

**Forward Process**: Gradually add Gaussian noise to data `x₀` over T timesteps:
```
q(x_t | x_{t-1}) = N(x_t; √(1-β_t) x_{t-1}, β_t I)
```

**Reverse Process**: Learn to denoise — a neural network (typically U-Net) predicts the noise at each step:
```
p_θ(x_{t-1} | x_t) = N(x_{t-1}; μ_θ(x_t, t), σ_t² I)
```

**Reparameterization Trick**: Sample `x_t` directly from `x₀` at any timestep:
```
x_t = √ᾱ_t x₀ + √(1-ᾱ_t) ε,   ε ~ N(0, I)
```

**Classifier-Free Guidance (CFG)**: During sampling, interpolate between conditional and unconditional predictions to control generation quality vs diversity:
```
ε̂ = ε_uncond + w · (ε_cond - ε_uncond)
```

**Latent Diffusion (Stable Diffusion)**: Run diffusion in compressed latent space (via VAE encoder) rather than pixel space — dramatically reduces compute.

**Strengths**: State-of-the-art image/video generation, mode coverage, controllable.
**Weaknesses**: Slow sampling (many denoising steps), DDIM/DDPM distillation needed for speed.

---

## 5. Generative Adversarial Networks (GANs)

- **Generator G**: Maps noise z → fake data.
- **Discriminator D**: Classifies real vs. generated.
- Minimax game: `min_G max_D E[log D(x)] + E[log(1 - D(G(z)))]`
- **Strengths**: Sharp image generation, fast single-pass synthesis.
- **Weaknesses**: Training instability (mode collapse), hard to optimize, no explicit density estimation.
- Variants: StyleGAN, ProGAN, BigGAN.

---

## 6. Variational Autoencoders (VAE)

- **Encoder**: Maps input x → latent distribution q(z|x) = N(μ, σ²).
- **Decoder**: Reconstructs from sampled z ~ q(z|x).
- **Loss**: Reconstruction + KL divergence to prior N(0, I).
- **Strengths**: Smooth latent space, principled probabilistic framework, controllable generation.
- **Weaknesses**: Blurry outputs (due to pixel-level reconstruction loss), posterior collapse.

---

## 7. Autoregressive Models

- Factorize joint distribution as product of conditionals: `p(x) = ∏ p(x_i | x_{<i})`.
- GPT-family, pixel-CNN, WaveNet, Transformer-XL.
- **Strengths**: Exact likelihood computation, strong sequence modeling.
- **Weaknesses**: Sequential generation (slow), left-to-right bias.

---

## 8. Flow Matching / Normalizing Flows

- Learn an invertible transformation f: data x → simple distribution z (e.g., Gaussian).
- Density computed exactly via change-of-formula: `log p(x) = log p(z) - log|det ∂f/∂x|`.
- **Flow Matching**: Train a vector field v_θ to transport data distribution to noise distribution along straight-line paths.
- **Strengths**: Exact density estimation, fast sampling, stable training.
- **Weaknesses**: Architecture constraints (invertibility), limited expressiveness per layer.

---

## Architecture Comparison

| Architecture | Scaling | Generation | Density Estimation | Long Sequences | Training Stability |
|---|---|---|---|---|---|
| Transformer | O(n²) | Autoregressive | ✗ (approx) | Limited by context | Stable |
| Mamba/SSM | O(n) | Recurrent | ✗ | ✓ Excellent | Stable |
| MoE | Sparse O(n²) | Depends on backbone | Depends | Limited by backbone | Load-balance sensitive |
| Diffusion | Multi-step | Iterative denoise | ✗ | N/A (spatial) | Stable |
| GAN | Single-pass | Generator | ✗ | N/A | Unstable (mode collapse) |
| VAE | Single-pass | Decoder | ✓ (ELBO) | Limited | Stable |
| Flow Matching | Single-pass | Invertible | ✓ Exact | Architecture-limited | Stable |
