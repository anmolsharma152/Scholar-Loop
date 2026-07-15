---
topic: papers
difficulty: hard
last_sent:
review_count: 0
tags:
  - paper
  - scaling-laws
  - kaplan
---

# Scaling Laws for Neural Language Models (Kaplan)

**Authors:** Jared Kaplan, Sam McCandlish, Tom Henighan, et al. (OpenAI)
**Published:** arXiv 2020 (2001.08361)

## Problem & Motivation

Language model performance follows predictable power-law relationships with model size, dataset size, and compute budget, but prior work did not disentangle these factors or determine optimal allocation of resources between model size and training data.

## Key Idea

Performance (test loss L) follows power laws in three regimes:

- **Fixed dataset:** L(N) = ((N_c/N)^α_N) + L_∞, where N is non-embedding model parameters, α_N ≈ 0.076
- **Fixed model:** L(D) = ((D_c/D)^α_D) + L_∞, where D is dataset size in tokens, α_D ≈ 0.095
- **Fixed compute:** L(C) = ((C_c/C)^α_C) + L_∞, where C is total FLOPs, α_C ≈ 0.050

Power-law scaling appears over 7 orders of magnitude for all three factors. When compute C is optimally split between model size N and dataset size D, the optimal split follows: N_opt ∝ C^0.73, D_opt ∝ C^0.27.

This means larger compute budgets should be spent primarily on larger models (model size ~10× for every 100× increase in compute). Model size matters more than dataset size: doubling model size reduces loss by more than doubling training data, until the dataset becomes impractically small relative to model capacity.

## Key Contributions

1. Universal power-law scaling for language model performance across 7 orders of magnitude
2. Principled framework for resource allocation between model size and training data
3. Discovery that model size matters more than dataset size for fixed compute

## Results

- Power-law exponents: α_N ≈ 0.076, α_D ≈ 0.095, α_C ≈ 0.050
- Optimal scaling: N_opt ∝ C^0.73, D_opt ∝ C^0.27
- GPT-3 175B trained on ~300B tokens (sub-optimal ratio ~0.57 tokens/param)

## Limitations

1. Power-law relationships hold for average test loss but may not predict performance on specific downstream tasks
2. Analysis used a single learning rate schedule that may have introduced systematic bias toward larger models
3. Real-world training involves data quality, which is not captured by token count alone
