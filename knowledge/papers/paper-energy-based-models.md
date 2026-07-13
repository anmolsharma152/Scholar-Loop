---
topic: papers
difficulty: hard
tags: [paper, energy-based-models, generative-models, diffusion, score-matching, likelihood]
last_sent:
review_count: 0
---

# Learning Energy-Based Models by Diffusion Recovery Likelihood

## Problem & Motivation
Training energy-based models (EBMs) traditionally requires contrastive divergence (CD), which is expensive and suffers from approximation errors in MCMC sampling. The key question: can we train EBMs without MCMC while achieving high likelihoods and good sample quality? The paper proposes using diffusion recovery likelihood (DRL) to bypass the need for expensive Langevin dynamics during training.

## Key Idea / Architecture
**Recovery Likelihood**: Instead of maximizing data likelihood directly, the model learns to recover clean data from noisy versions:
1. Start with clean data x₀
2. Apply forward diffusion: add noise over T steps → x_T (Gaussian)
3. Model learns to reverse this process: given xₜ and t, predict xₜ₋₁
4. Each step is a conditional EBMs: p(xₜ₋₁|xₜ) = exp(-E(xₜ₋₁,xₜ,t)) / Z(xₜ,t)

**Training**: Standard cross-entropy on denoised predictions, no MCMC needed
**Sampling**: Run Langevin dynamics at each denoising step

The energy function E(xₜ₋₁,xₜ,t) models the compatibility between consecutive steps. The model has separate architectures for the conditioning (xₜ) and the variable (xₜ₋₁), enabling efficient conditional sampling.

## Key Contributions
- Diffusion Recovery Likelihood: training EBMs without MCMC
- Energy function decomposed into conditioning and variable components
- Achieved state-of-the-art likelihoods on standard image benchmarks
- Competitive sample quality with GANs and VAEs
- Unified framework connecting EBMs, diffusion models, and denoising score matching
- Demonstrated that EBMs can be competitive with modern generative models when trained properly

## Results
- **CIFAR-10**: 2.97 bits/dim (likelihood), competitive sample quality
- **CelebA-HQ**: 1.33 bits/dim, high-quality generated samples
- **ImageNet 32×32**: State-of-the-art likelihood among EBMs
- **Training efficiency**: No MCMC during training; faster than CD-based methods
- **Sample quality**: Comparable to or better than GANs on perceptual metrics
- **Likelihood**: Outperforms standard EBMs trained with contrastive divergence by significant margins

## Why It Matters / Impact
This paper demonstrated that energy-based models—once considered difficult to train—can be competitive with modern generative models when trained with diffusion recovery likelihood. The work bridges EBMs and diffusion models, showing they are more closely related than previously understood. The training approach eliminates the expensive MCMC sampling that plagued EBM training, making them practical for large-scale applications. The insights influenced subsequent work on score-based generative models and denoising diffusion models.

## Weaknesses / Limitations
- Sampling still requires Langevin dynamics at each denoising step (slow inference)
- Energy function design is architecture-specific; generalization is unclear
- The conditional EBM formulation adds complexity compared to simpler diffusion models
- No analysis of mode coverage or diversity metrics
- Limited to image data; no evaluation on other modalities
- The connection to score matching is noted but not fully explored theoretically
