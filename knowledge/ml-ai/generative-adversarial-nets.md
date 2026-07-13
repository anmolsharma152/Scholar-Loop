---
difficulty: hard
last_sent: 2026-07-13 23:37:23.725348+00:00
review_count: 1
sources:
- GAN-LectureNotes.pdf
- CycleGAN.pdf
- GAN-LECTURE.pdf (Masai)
- Generative Adversarial Networks.pdf (Masai)
- GANs with contemporary advances and applications.pdf (Masai)
tags:
- dl
- gan
- generative
topic: ml-ai
---

# Generative Adversarial Networks (GANs)

## Core Concept

- GANs transform distributions: sample from Gaussian `z ~ N(0, I)`, map through Generator to produce data-like samples
- **Generator (G)**: Takes random noise z, produces fake samples trying to fool D
- **Discriminator (D)**: Binary classifier distinguishing real training data from G's fakes
- "The most interesting idea in the last 10 years in machine learning" — Yann LeCun

## Generative vs Discriminative Models

- **Generative**: Model distribution of individual classes `P(X|Y)` or `P(X)`
- **Discriminative**: Learn decision boundary between classes `P(Y|X)`
- GANs are generative: they learn to produce data from a learned distribution

## Adversarial Loss

```
min_G max_D V(D,G) = E_{x~p_data}[log D(x)] + E_{z~p_z}[log(1 - D(G(z)))]
```

- D tries to maximize: correctly classify real vs fake
- G tries to minimize: fool D into classifying fakes as real
- **Nash equilibrium**: G produces perfect samples, D outputs 0.5 everywhere

## Training Challenges

- **Mode collapse**: G produces limited variety, covering only a few modes of data distribution
- **Non-convergence**: Oscillating losses, training instability
- **Vanishing gradients**: When D is too strong, G gets no useful gradient signal
- **Evaluation difficulty**: No explicit likelihood; must use proxy metrics

## DCGAN (Deep Convolutional GAN)

- Replaces FC layers with strided convolutions (D) and transposed convolutions (G)
- Batch normalization in both G and D
- Architecture guidelines: ReLU in G (except output uses tanh), LeakyReLU in D
- Stable training via architectural constraints rather than loss modifications

## Conditional GAN (cGAN)

- Both G and D receive auxiliary information (class label, text, etc.)
- `G(z, c)` and `D(x, c)` — conditioning enables controlled generation
- Applications: class-specific image generation, text-to-image

## CycleGAN (Unpaired Image Translation)

- **Problem**: Paired training data unavailable (e.g., no horse↔zebra pairs)
- **Dual generator system**: `G: X→Y` and `F: Y→X`
- **Three loss components**:
  1. **Adversarial losses** (forward and backward): Each G fools corresponding D
  2. **Cycle consistency loss**: `F(G(x)) ≈ x` and `G(F(y)) ≈ y`
  3. **Identity loss** (optional): Preserves color composition when input already in target domain
- **Easy path principle**: Cycle consistency forces G to learn meaningful translation rather than mode collapse
- Trained end-to-end, symmetric architecture

## Evaluation Metrics

- **FID (Fréchet Inception Distance)**: Measures distance between feature distributions of real and generated images (lower = better)
- **IS (Inception Score)**: Measures quality and diversity of generated images (higher = better)

## Key Takeaway

- GANs learn distribution transformations, not point-to-point mappings
- Fundamental difference from autoencoders: GANs sample from transformed distribution; autoencoders deterministically map inputs