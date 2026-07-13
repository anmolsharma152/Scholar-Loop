---
topic: ml-ai
difficulty: hard
tags: [dl, diffusion, generative]
sources:
  - DiffusionModel-DDPM.pdf
---

# Diffusion Models

## Overview

- State-of-the-art for generating diverse, high-resolution images
- Fundamentally different from GANs: decompose generation into smaller denoising steps
- Large-scale successful models: GLIDE, DALL-E 2/3, Imagen
- Key reference: Ho et al., "Denoising Diffusion Probabilistic Models" (2020)

## Forward Process (Diffusion)

- Gradually adds Gaussian noise to data over T timesteps
- `q(x_t | x_{t-1}) = N(x_t; √(1-β_t)·x_{t-1}, β_t·I)`
- Noise schedule `{β_t}` controls how much noise added at each step
- At sufficient T, `x_T` becomes pure Gaussian noise
- Forward process is fixed (no learning) — defined by the noise schedule

## Reverse Process (Denoising)

- Learns to reverse the noising process: recover `x_{t-1}` from `x_t`
- `p_θ(x_{t-1} | x_t) = N(x_{t-1}; μ_θ(x_t, t), Σ_θ(x_t, t))`
- Neural network predicts the noise ε added at each step
- Training objective: `L = E[||ε - ε_θ(x_t, t)||²]` (simplified noise prediction loss)
- Iterative refinement: start from noise, denoise step by step to generate

## DDPM (Denoising Diffusion Probabilistic Models)

- **Forward**: `x_t = √ᾱ_t · x_0 + √(1-ᾱ_t) · ε` where `ε ~ N(0,I)` and `ᾱ_t = ∏(1-β_s)` for s=1..t
- **Reverse**: Network ε_θ(x_t, t) predicts the noise component
- **Training**: Sample random t, add noise, predict it; loss is MSE between true and predicted noise
- **Sampling**: Start from `x_T ~ N(0,I)`, iteratively apply reverse process

## U-Net Architecture for Diffusion

- Encoder-decoder with skip connections (U-Net backbone)
- **Time embedding**: Sinusoidal positional encoding of timestep t, added/embedded into features
- **Self-attention layers**: Applied at specific resolutions for global coherence
- **Residual blocks**: With group normalization and SiLU/Swish activation

## Noise Schedule

- Linear schedule: `β_t` increases linearly from `β_min` to `β_max`
- Cosine schedule: Smoother noise addition, better for high-resolution
- Controls the tradeoff between training stability and sample quality

## DDIM (Denoising Diffusion Implicit Models)

- Non-Markovian reverse process — enables faster sampling
- Can skip steps: generate in 10-50 steps instead of 1000+
- Deterministic mapping: same noise always produces same output
- Stochastic variant: still allows randomness for diversity

## Text Conditioning

- Text encoded via pretrained language model (CLIP, T5, etc.)
- **Cross-attention**: Text features attend to spatial features in U-Net
- Each attention layer: queries from image features, keys/values from text embeddings
- Enables text-to-image generation

## Classifier-Free Guidance

- Train both conditional and unconditional models simultaneously
- At inference: `ε̃ = ε_uncond + w · (ε_cond - ε_uncond)`
- `w` (guidance scale) controls tradeoff: higher w = more fidelity to text, less diversity
- `w=1` is standard conditional generation; `w>1` amplifies conditioning

## Latent Diffusion (Stable Diffusion)

- **Key insight**: Run diffusion in latent space, not pixel space
- VAE encoder compresses image to low-dimensional latent `z`
- Diffusion operates on `z` (much smaller, cheaper)
- VAE decoder reconstructs pixels from denoised latent
- **Dramatic efficiency gain**: 512×512 images become 64×64 latents
- Architecture: VAE encoder → U-Net in latent space → VAE decoder
