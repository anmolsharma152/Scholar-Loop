---
topic: papers
difficulty: hard
tags: [paper, gan, generative-models, adversarial-training, deep-learning]
---

# Generative Adversarial Nets

**Authors:** Goodfellow et al. (Université de Montréal)
**Published:** NeurIPS 2014
**arXiv:** 1406.2661

## Problem & Motivation

Generative modeling aims to learn the distribution of training data and generate new samples from it. Existing approaches had limitations:
1. **Explicit density models** - Required defining tractable density functions
2. **Variational methods** - Lower bounds on likelihood, not direct generation
3. **Markov chains** - Computationally expensive sampling

The question: can we train generative models without explicitly computing the data density?

## Key Idea / Architecture

### Adversarial Framework

GAN uses a minimax game between two networks:

**Generator (G):** Maps random noise z to data space
- Input: $z \sim p_z(z)$ (typically Gaussian)
- Output: $G(z)$ (synthetic data)

**Discriminator (D):** Classifies real vs generated data
- Input: Data sample x
- Output: $D(x)$ (probability that x is real)

### Minimax Game

The training objective is:

$$\min_G \max_D V(D, G) = \mathbb{E}_{x \sim p_{data}}[\log D(x)] + \mathbb{E}_{z \sim p_z}[\log(1 - D(G(z)))]$$

**Discriminator's goal:** Maximize this (correctly classify real and fake)
**Generator's goal:** Minimize this (make discriminator confused)

### Training Algorithm

```
For each training iteration:
  1. Sample real data batch {x_1, ..., x_m} from training set
  2. Sample noise batch {z_1, ..., z_m} from p_z
  3. Generate fake data {G(z_1), ..., G(z_m)}
  4. Update D by ascending: log D(x) + log(1 - D(G(z)))
  5. Sample new noise batch
  6. Update G by descending: log(1 - D(G(z)))
```

In practice, generator is updated with $\log D(G(z))$ instead of $\log(1-D(G(z)))$ to avoid vanishing gradients.

## Key Contributions

1. **Adversarial training framework** - Novel way to train generative models
2. **Implicit density estimation** - No need to compute data likelihood
3. **Simple and elegant** - Only need to backprop through both networks
4. **Theoretical foundation** - Proves that optimal D and global optimum of G exist

## Results

- **MNIST:** Visual quality competitive with real digits
- **Toronto Face Database:** Generated realistic faces
- **CIFAR-10:** Learned to generate recognizable objects
- **Comparison:** Better visual quality than RBMs and deep belief networks

### Theoretical Results

1. **Optimal discriminator:** $D^*_G(x) = \frac{p_{data}(x)}{p_{data}(x) + p_g(x)}$
2. **Global optimum:** When $p_g = p_{data}$, $V(D^*, G^*) = -\log 4$
3. **No mode collapse at optimum:** The generator learns the true data distribution

## Why It Matters

GANs revolutionized generative modeling:

1. **Photo-realistic generation** - Led to StyleGAN, BigGAN for high-quality images
2. **Image-to-image translation** - CycleGAN, Pix2Pix
3. **Super-resolution** - SRGAN, ESRGAN
4. **Data augmentation** - Generate synthetic training data
5. **Art and creativity** - Enabled AI art and creative applications

## Weaknesses

- **Mode collapse** - Generator produces limited variety of outputs
- **Training instability** - Hard to balance G and D training
- **No explicit density** - Can't compute likelihood or evaluate generation quality directly
- **Evaluation difficulty** - FID and IS are imperfect metrics
- **Training divergence** - Networks can fail to converge

## Follow-up Work

- **DCGAN:** Convolutional architecture for stable training
- **WGAN:** Wasserstein distance for better training stability
- **StyleGAN:** Style-based generator for high-quality faces
- **CycleGAN:** Unpaired image-to-image translation
- **Diffusion models:** Later surpassed GANs in generation quality