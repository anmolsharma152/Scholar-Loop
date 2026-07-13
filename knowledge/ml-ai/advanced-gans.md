---
topic: ml-ai
difficulty: hard
tags: [dl, gan, advanced]
sources:
  - GAN-LectureNotes.pdf
  - CycleGAN.pdf
  - Advanced Generative Adversarial Networks.pdf (Masai)
  - GANs with contemporary advances and applications.pdf (Masai)
  - GAN-LECTURE.pdf (Masai)
---

# Advanced GANs

## Wasserstein GAN (WGAN)

- **Core idea**: Replace JS-divergence with Earth Mover (Wasserstein) distance
- **Earth Mover distance**: Minimum cost to transform one distribution into another
- **WGAN loss**: `L = E[D(x)] - E[D(G(z))]` (critic, not discriminator)
- **Lipschitz constraint**: Enforced via weight clipping or gradient penalty
- **Benefits**: Meaningful loss curves, stable training, no mode collapse

### WGAN-GP (Gradient Penalty)

- Replaces weight clipping with gradient penalty
- `L_gp = λ · E[(||∇_x̂ D(x̂)||₂ - 1)²]` where `x̂ = εx + (1-ε)G(z)`
- Enforces 1-Lipschitz constraint smoothly
- Better training stability than weight clipping

## Progressive GAN (ProGAN)

- **Progressive growing**: Train with low resolution first, progressively add layers
- Training: 4×4 → 8×8 → 16×16 → ... → 1024×1024
- Fade-in new layers with residual connection during transition
- Enables training of very high-resolution GANs (1024×1024)
- First to produce photorealistic faces

## StyleGAN

- **Mapping network**: z → w (8-layer MLP) maps latent code to intermediate space
- **Style modulation**: w controls AdaIN (Adaptive Instance Normalization) at each layer
- **Style mixing**: Different w values for different layers → control coarse/fine/medium features
- **Noise injection**: Per-pixel noise added at each layer for stochastic variation

### Key Innovations

- **Coarse styles** (low resolution): Pose, face shape, glasses
- **Medium styles** (mid resolution): Facial features, eye shape
- **Fine styles** (high resolution): Color scheme, lighting details
- **Stochastic variation**: Hair strands, pores, background details via noise

### Benefits

- **Interpretability**: Latent space disentangled — different regions control different attributes
- **Control granularity**: Fine-grained attribute manipulation
- **Applications**: Face editing, style transfer, art generation

## BigGAN

- Large-scale GAN training with class conditioning
- **Tricks**: Larger batch sizes, class-conditional, truncated latent truncation
- State-of-the-art ImageNet generation quality
- Class-conditional generation with high fidelity

## SRGAN (Super-Resolution GAN)

- GAN for single-image super-resolution
- **Generator**: Maps low-res → high-res with perceptual loss + adversarial loss
- **Perceptual loss**: Feature-space distance in VGG, not pixel-space MSE
- Produces sharper, more perceptually realistic upscaled images
- Loss: `L = L_pixel + λ₁·L_perceptual + λ₂·L_adversarial`

## Conditional Generation & Text-to-Image

### StackGAN (2-Stage)

1. **Stage 1**: Generate 64×64 from text — captures structural information
2. **Stage 2**: Upsample to 256×256 — adds photorealistic detail
- Both stages conditioned on same text embedding
- Text encoding via pretrained model, conditioned via conditioning augmentation

### Pix2Pix (Paired Image Translation)

- **Problem**: Paired training data (e.g., edges↔photos)
- **Loss**: `L = L_GAN + λ·L_L1` (adversarial + reconstruction)
- Generator: U-Net; Discriminator: PatchGAN
- Condition is the input image itself

## Architecture Comparison

| Model | Key Innovation | Use Case |
|-------|---------------|----------|
| WGAN | Wasserstein distance | Stable training |
| ProGAN | Progressive growing | High-res generation |
| StyleGAN | Mapping network + AdaIN | Controllable generation |
| BigGAN | Scale + class conditioning | ImageNet synthesis |
| SRGAN | Perceptual loss | Super-resolution |
| StackGAN | Two-stage text-to-image | Text-to-photo |
| Pix2Pix | Paired translation | Image-to-image |
| CycleGAN | Cycle consistency | Unpaired translation |
