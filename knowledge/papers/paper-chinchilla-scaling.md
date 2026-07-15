---
topic: papers
difficulty: hard
last_sent:
review_count: 0
tags:
  - paper
  - scaling-laws
  - chinchilla
---

# Training Compute-Optimal Large Language Models (Chinchilla)

**Authors:** Jordan Hoffmann, Sebastian Borgeaud, Arthur Mensch, et al. (DeepMind)
**Published:** arXiv 2022 (2203.15556)

## Problem & Motivation

Kaplan et al.'s optimal scaling was systematically biased: they recommended models too large for their datasets, resulting in under-trained, over-parameterized models. The question was whether optimal performance required ever-larger models or whether training existing models longer on more data was more effective.

## Key Idea

The Chinchilla scaling laws are:
- N_opt ∝ C^0.50 (equal allocation between model and data)
- D_opt ∝ C^0.50

This contradicts Kaplan et al.'s N_opt ∝ C^0.73, D_opt ∝ C^0.27 recommendation. The key insight is that the learning rate schedule divides training into a "compute efficient" phase (loss decreasing as power law) and an "irreversible" phase (loss decreasing linearly with tokens). Optimal allocation places the model at the transition between these phases.

## Chinchilla Validation

The Chinchilla model (70B parameters, 1.4T tokens) is compared against Gopher (280B parameters, 300B tokens). Both trained on the same compute budget (~5.0×10^23 FLOPs). Chinchilla achieves better performance across:

- MMLU: 67.5% vs. 60.0% (+7.5 points)
- BIG-Bench (average): Chinchilla outperforms Gopher on 69% of tasks
- StoryCloze: 80.8% vs. 78.5% (+2.3 points)
- WinRate: 70.1% vs. 64.6% (+5.5 points)
- GSM8K: 52.4% vs. 40.5% (+11.9 points)

## Key Contributions

1. Demonstration that the optimal scaling ratio is 1:1 between model parameters and training tokens
2. Empirical validation that a 70B model trained on 1.4T tokens outperforms a 280B model trained on 300B tokens at the same compute cost
3. Unified framework for predicting performance of models of any size trained on any dataset size

## Impact

The Chinchilla scaling laws fundamentally changed how companies train large language models. Before Chinchilla, the field pursued ever-larger models (GPT-3 175B, PaLM 540B). After Chinchilla, the focus shifted to training smaller models much longer (Llama-2 70B on 2T tokens, Mistral 7B). This reduced inference cost while maintaining quality.

## Limitations

1. The 1:1 optimal ratio assumes a fixed compute budget and does not account for inference cost
2. Analysis is limited to decoder-only Transformer architectures
3. Real-world training involves data quality, which varies enormously and is not captured by token count alone
