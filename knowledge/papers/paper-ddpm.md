---
topic: papers
difficulty: hard
tags: [paper, diffusion-models, denoising, score-matching, generative-models, image-synthesis, langevin-dynamics]
---

# Denoising Diffusion Probabilistic Models (DDPM)

## Problem & Motivation

- Deep generative models (GANs, VAEs, flows) have achieved high quality samples
- Diffusion models: Simple to define, efficient to train, but no demonstration of high quality samples
- Need to bridge gap between diffusion model theory and practical sample quality
- Goal: Show diffusion models can generate high-quality images

## Key Idea / Architecture

### Forward Process (Diffusion)
- Gradually adds Gaussian noise to data over T timesteps
- q(xt|xt−1) = N(xt; √(1−βt) xt−1, βt I)
- βt schedule: linearly increasing from 10⁻⁴ to 0.02
- Closed-form sampling: q(xt|x0) = N(xt; √ᾱt x0, (1−ᾱt)I)

### Reverse Process (Denoising)
- Learned Markov chain starting from noise p(xT) = N(0, I)
- pθ(xt−1|xt) = N(xt−1; μθ(xt, t), σt² I)
- U-Net backbone with group normalization
- Time embedding via Transformer sinusoidal position embedding
- Self-attention at 16×16 resolution

### Key Insight: ε-prediction Parameterization
- Instead of predicting μ̃t, predict noise ε
- μθ(xt, t) = (1/√αt)(xt − √(βt/(1−ᾱt)) εθ(xt, t))
- Resembles Langevin dynamics with learned score
- Simplified training objective: Lsimple = Et,x0,ε [‖ε − εθ(√ᾱt x0 + √(1−ᾱt) ε, t)‖²]

### Variational Bound Decomposition
```
L = LT + Σt>1 Lt−1 + L0
```
- LT: Forward process entropy (constant, ignored)
- Lt−1: KL divergence between forward posterior and reverse process
- L0: Discrete decoder log-likelihood

## Key Contributions

### 1. State-of-the-Art FID on CIFAR10
- Unconditional FID: 3.17 (beats most conditional models)
- Inception Score: 9.46 ± 0.11
- Better than StyleGAN2 on some metrics

### 2. Connection to Denoising Score Matching
- ε-prediction objective resembles denoising score matching
- Training is equivalent to variational inference for Langevin-like sampler
- Bridges diffusion models and score-based generative models

### 3. Progressive Lossy Decompression
- Diffusion process as progressive encoding/decoding
- Large-scale features appear first, details last
- Generalizes autoregressive decoding with arbitrary bit ordering

### 4. High-Quality LSUN Samples
- Bedroom FID: 4.90 (vs ProgressiveGAN 8.34)
- Church FID: 7.89 (vs StyleGAN 4.21)
- Competitive with GANs on 256×256 images

## Results (Specific Numbers)

### CIFAR10 Results
| Model | IS | FID | NLL (bits/dim) |
|-------|-----|-----|----------------|
| BigGAN | 9.22 | 14.73 | - |
| StyleGAN2+ADA | 10.06 | 2.67 | - |
| NCSNv2 | 8.06 | 13.22 | - |
| DDPM (L, fixed Σ) | 7.67 | 13.51 | ≤ 3.70 |
| DDPM (Lsimple) | 9.46 | 3.17 | ≤ 3.75 |

### LSUN 256×256 FID Scores
| Dataset | ProgressiveGAN | StyleGAN | StyleGAN2 | DDPM |
|---------|---------------|----------|-----------|------|
| Bedroom | 8.34 | 2.65 | - | 4.90 |
| Church | 6.42 | 4.21 | 3.86 | 7.89 |
| Cat | 37.52 | 8.53 | 6.93 | 19.75 |

### Rate-Distortion Analysis (CIFAR10)
| Reverse Steps | Rate (bits/dim) | Distortion (RMSE) |
|--------------|-----------------|-------------------|
| 1000 | 1.776 | 0.951 |
| 800 | 1.830 | 18.475 |
| 600 | 1.845 | 30.809 |
| 400 | 1.852 | 46.128 |
| 200 | 1.856 | 60.972 |

### Ablation: Reverse Process Parameterization
| Objective | IS | FID |
|-----------|-----|-----|
| μ̃ prediction (baseline, true VB) | 7.67 | 13.51 |
| ε prediction (Lsimple) | 9.46 | 3.17 |
| L, learned diagonal Σ | - | unstable |

## Why It Matters / Impact

1. **Paradigm shift**: Established diffusion models as competitive with GANs
2. **Foundation for modern generative AI**: Led to DALL-E 2, Imagen, Stable Diffusion
3. **Score matching connection**: Unified framework for understanding generative models
4. **Progressive generation**: Enabled controllable generation at different scales
5. **Interpolation quality**: Smooth latent space interpolations

## Weaknesses / Limitations

1. **Slow sampling**: Requires 1000 neural network evaluations
2. **Log-likelihood gap**: Not competitive with autoregressive models
3. **Memory intensive**: U-Net with self-attention requires significant GPU memory
4. **Training cost**: 10.6 hours on TPU v3-8 for CIFAR10
5. **Limited 256×256 quality**: LSUN results still behind best GANs

## Follow-up Work

- DDIM: Accelerated sampling with deterministic process
- Improved DDPM: Better noise schedule, learned variances
- Score-based SDE: Continuous-time diffusion framework
- Latent Diffusion: Diffusion in compressed latent space (Stable Diffusion)
- Consistency Models: Single-step generation from diffusion
