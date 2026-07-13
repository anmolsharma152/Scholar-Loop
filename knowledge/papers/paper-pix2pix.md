---
topic: papers
difficulty: hard
tags: [paper, pix2pix, conditional-gan, image-to-image-translation, patchgan, u-net, structured-prediction]
---

# Image-to-Image Translation with Conditional Adversarial Networks

## Problem & Motivation

- Many vision problems involve translating input images to output images
- Each task traditionally tackled with separate, special-purpose machinery
- Euclidean distance minimization produces blurry results (averages plausible outputs)
- Need: Learn loss function automatically from data, not hand-engineer per task

## Key Idea / Architecture

### Conditional GAN Framework
- Generator G: {x, z} → y (maps input image + noise to output)
- Discriminator D: classifies real vs fake {input, output} pairs
- Both observe input x (unlike unconditional GAN)

### Generator: U-Net Architecture
- Encoder-decoder with skip connections between mirrored layers
- Skip connections concatenate all channels at layer i with layer n-i
- Allows low-level information to bypass bottleneck
- Critical: Without skip connections, encoder-decoder fails to learn realistic images

### Discriminator: PatchGAN
- Classifies if each N×N patch is real or fake
- Runs convolutionally across image, averages responses
- 70×70 receptive field works best across tasks
- Models image as Markov random field (assumes patch independence)

### Training Objective
```
G* = arg min_G max_D LcGAN(G, D) + λLL1(G)
```
- LcGAN: Standard conditional GAN loss
- LL1: L1 distance between predicted and ground truth (λ=100)
- L1 preferred over L2 (less blurring)

## Key Contributions

### 1. General-Purpose Solution
- Same architecture and objective for all tasks
- Simply train on different data for different problems
- Tasks: labels↔photo, edges→photo, BW→color, day→night, etc.

### 2. Learned Loss Function
- GAN learns to penalize any structure differing between output and target
- No need to hand-design loss per application
- cGAN produces sharp images; L1 ensures low-frequency correctness

### 3. Data Efficiency
- Facade training: only 400 images
- Day to night: only 91 webcams
- Training < 2 hours on single GPU for small datasets
- Test time: < 1 second per image

### 4. Fully-Convolutional Translation
- Train on 256×256, test on arbitrary sizes
- PatchGAN applied convolutionally to larger images
- Enables high-resolution inference without retraining

## Results (Specific Numbers)

### FCN-Score on Cityscapes (Labels→Photos)
| Loss | Per-pixel Acc. | Per-class Acc. | Class IOU |
|------|---------------|----------------|-----------|
| L1 | 0.42 | 0.15 | 0.11 |
| GAN | 0.22 | 0.05 | 0.01 |
| cGAN | 0.57 | 0.22 | 0.16 |
| L1+GAN | 0.64 | 0.20 | 0.15 |
| L1+cGAN | 0.66 | 0.23 | 0.17 |
| Ground truth | 0.80 | 0.26 | 0.21 |

### Generator Architecture Comparison
| Architecture | Per-pixel Acc. | Class IOU |
|-------------|---------------|-----------|
| Encoder-decoder (L1) | 0.35 | 0.08 |
| Encoder-decoder (L1+cGAN) | 0.29 | 0.05 |
| U-Net (L1) | 0.48 | 0.13 |
| U-Net (L1+cGAN) | 0.55 | 0.14 |

### Discriminator Receptive Field
| Receptive Field | Per-pixel Acc. | Class IOU |
|----------------|---------------|-----------|
| 1×1 (PixelGAN) | 0.39 | 0.10 |
| 16×16 | 0.65 | 0.17 |
| 70×70 (PatchGAN) | 0.66 | 0.17 |
| 286×286 (ImageGAN) | 0.42 | 0.11 |

### AMT Perceptual Studies
| Task | Method | % Turkers Labeled Real |
|------|--------|----------------------|
| Map→Photo | L1+cGAN | 18.9% ± 2.5% |
| Photo→Map | L1+cGAN | 6.1% ± 1.3% |
| Colorization | L1+cGAN | 22.5% ± 1.6% |

### Color Distribution Matching
| Loss | Histogram Intersection (a) | (b) | (c) |
|------|---------------------------|------|------|
| L1 | 0.81 | 0.69 | 0.70 |
| cGAN | 0.87 | 0.74 | 0.84 |
| L1+cGAN | 0.86 | 0.84 | 0.82 |

## Why It Matters / Impact

1. **Unified framework**: Same approach for diverse image translation tasks
2. **Learned losses**: Paradigm shift from hand-designed to learned objectives
3. **Community impact**: Widely adopted for artistic and practical applications
4. **Foundation for CycleGAN**: Enabled unpaired image-to-image translation
5. **Influenced downstream work**: SPADE, SPADE-GAN, StyleGAN-based editing

## Weaknesses / Limitations

1. **Limited stochasticity**: Generator learns to ignore noise input (uses dropout instead)
2. **Mode collapse risk**: Unconditional GAN variant produces same output regardless of input
3. **70×70 limitation**: Optimal patch size may not capture all structure
4. **Training instability**: GAN training requires careful balancing
5. **No quantitative evaluation**: Perceptual studies are subjective

## Follow-up Work

- CycleGAN: Unpaired image-to-image translation
- SPADE/GauGAN: Semantic image synthesis
- pix2pixHD: High-resolution image synthesis
- MUNIT: Multimodal unsupervised image-to-image translation
- CUT: Contrastive learning for unpaired translation
