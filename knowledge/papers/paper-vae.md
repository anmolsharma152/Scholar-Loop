---
topic: papers
difficulty: hard
tags: [paper, vae, variational-autoencoder, generative-models, deep-learning]
---

# Auto-Encoding Variational Bayes

**Authors:** Kingma & Welling (University of Amsterdam)
**Published:** ICLR 2014
**arXiv:** 1312.6114

## Problem & Motivation

Deep generative models aim to learn the data distribution $p(x)$ and generate new samples. Existing approaches:
1. **Maximum likelihood** - Tractable for some models (RBMs) but not deep directed models
2. **Wake-sleep** - Unstable and biased
3. **Monte Carlo methods** - Computationally expensive

The question: can we train deep directed generative models using variational inference?

## Key Idea / Architecture

### Variational Autoencoder (VAE)

**Generative model:**
- Latent variable $z \sim p(z) = \mathcal{N}(0, I)$
- Decoder: $p_\theta(x|z)$ generates data from latent code

**Inference model:**
- Encoder: $q_\phi(z|x)$ approximates true posterior $p(z|x)$
- Maps data to latent distribution

### Variational Lower Bound (ELBO)

Maximize the evidence lower bound:

$$\mathcal{L}(\theta, \phi; x) = \mathbb{E}_{q_\phi(z|x)}[\log p_\theta(x|z)] - D_{KL}(q_\phi(z|x) || p(z))$$

**Reconstruction term:** $\mathbb{E}_{q_\phi(z|x)}[\log p_\theta(x|z)]$
- Measures how well the decoder reconstructs the input

**KL divergence term:** $D_{KL}(q_\phi(z|x) || p(z))$
- Regularizes the latent space to be close to prior

### Reparameterization Trick

To backprop through sampling, reparameterize:

$$z = \mu + \sigma \cdot \epsilon, \quad \epsilon \sim \mathcal{N}(0, I)$$

where $\mu$ and $\sigma$ are outputs of the encoder.

### Architecture

**Encoder:**
- Input: x (e.g., image)
- Output: $\mu$ and $\log \sigma^2$ (latent distribution parameters)

**Decoder:**
- Input: z (sampled from encoder)
- Output: reconstructed x

## Key Contributions

1. **Variational inference for deep generative models** - Principled training framework
2. **Reparameterization trick** - Enables backpropagation through sampling
3. **Latent space regularization** - KL term ensures smooth, meaningful latent space
4. **End-to-end training** - Both encoder and decoder trained jointly

## Results

- **MNIST:** 0.31 nats (log-likelihood, competitive with other methods)
- **Frey Faces:** Good quality reconstructions and generations
- **Speech:** Generated realistic speech samples
- **Latent space:** Smooth interpolation between digits

### Properties of VAE

1. **Smooth latent space** - Interpolating between points generates meaningful samples
2. **Disentangled representations** - Different latent dimensions capture different factors
3. **Generation** - Can sample from prior and decode
4. **Reconstruction** - Can encode and reconstruct inputs

## Why It Matters

VAE was foundational for deep generative modeling:

1. **Principled framework** - Variational inference for deep learning
2. **Latent representations** - Useful for representation learning
3. **Foundation for diffusion** - Influenced later generative models
4. **Wide applications** - Used in many domains

## Weaknesses

- **Blurry samples** - Reconstruction loss leads to averaging
- **KL collapse** - Posterior can collapse to prior
- **Limited expressiveness** - Simple latent distributions
- **Evaluation difficulty** - Hard to evaluate generative models
- **Trade-off** - Reconstruction vs regularization balance

## Follow-up Work

- **β-VAE:** Disentangled representations
- **CVAE:** Conditional generation
- **VQ-VAE:** Discrete latent spaces
- **Hierarchical VAEs:** Multiple layers of latent variables
- **Diffusion models:** Later surpassed VAEs in sample quality