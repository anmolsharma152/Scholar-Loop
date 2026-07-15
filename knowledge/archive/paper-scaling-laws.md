---
topic: papers
difficulty: hard
last_sent:
review_count: 0
tags:
  - paper
  - scaling-laws
  - compute-optimal
  - chinchilla
  - large-language-models
---

# Scaling Laws for Neural Language Models + Training Compute-Optimal Large Language Models (Chinchilla)

**Authors:** (1) Jared Kaplan, Sam McCandlish, Tom Henighan, Tom B. Brown, Benjamin Chess, Rewon Child, Scott Gray, Alec Radford, Jeffrey Wu, Dario Amodei (OpenAI) — (2) Jordan Hoffmann, Sebastian Borgeaud, Arthur Mensch, Elena Buchatskaya, Trevor Cai, Eliza Rutherford, Diego de Las Casas, Lisa Anne Hendricks, Johannes Welbl, Aidan Clark, Tom Hennigan, Edward Nelse, Simon Osindero, Simon Carnell, Jack W. Rae, Sven Borgeaud, Laurent Sifre, Oriol Vinyals, Koray Kavukcuoglu, Raia Hadsell (DeepMind)
**Published:** (1) arXiv 2020; (2) arXiv 2022
**arXiv:** (1) 2001.08361; (2) 2203.15556

## Problem & Motivation

(Kaplan et al. 2020) Language model performance follows predictable power-law relationships with model size, dataset size, and compute budget, but prior work did not disentangle these factors or determine optimal allocation of resources between model size and training data. The field needed a principled framework for deciding whether to train a larger model on less data or a smaller model on more data given a fixed compute budget.

(Chinchilla, Hoffmann et al. 2022) Followed up by demonstrating that Kaplan et al.'s optimal scaling was systematically biased: they recommended models too large for their datasets, resulting in under-trained, over-parameterized models. The question was whether optimal performance required ever-larger models or whether training existing models longer on more data was more effective.

## Key Idea / Architecture

**(Kaplan et al. 2020):** Performance (test loss L) follows power laws in three regimes:
- **Fixed dataset:** L(N) = ((N_c/N)^α_N) + L_∞, where N is non-embedding model parameters, α_N ≈ 0.076, N_c is a characteristic scale
- **Fixed model:** L(D) = ((D_c/D)^α_D) + L_∞, where D is dataset size in tokens, α_D ≈ 0.095, D_c is a characteristic scale
- **Fixed compute:** L(C) = ((C_c/C)^α_C) + L_∞, where C is total FLOPs, α_C ≈ 0.050

Power-law scaling appears over 7 orders of magnitude for all three factors. When compute C is optimally split between model size N and dataset size D, the optimal split follows: N_opt ∝ C^0.73, D_opt ∝ C^0.27. This means larger compute budgets should be spent primarily on larger models (model size ~10× for every 100× increase in compute).

Model size matters more than dataset size: doubling model size reduces loss by more than doubling training data, until the dataset becomes impractically small relative to model capacity.

**(Chinchilla, Hoffmann et al. 2022):** Introduces a compute-optimal framework based on the final achievable test loss. The key insight is that the learning rate schedule divides training into a "compute efficient" phase (loss decreasing as power law) and an "irreversible" phase (loss decreasing linearly with tokens). Optimal allocation places the model at the transition between these phases.

The Chinchilla scaling laws are:
- N_opt ∝ C^0.50 (equal allocation between model and data)
- D_opt ∝ C^0.50

This contradicts Kaplan et al.'s N_opt ∝ C^0.73, D_opt ∝ C^0.27 recommendation.

**Chinchilla validation:** The Chinchilla model (70B parameters, 1.4T tokens) is compared against Gopher (280B parameters, 300B tokens). Both trained on the same compute budget (~5.0×10^23 FLOPs). Chinchilla achieves better performance across:
- MMLU: 67.5% vs. 60.0%
- BIG-Bench (average across tasks): Chinchilla outperforms Gopher on 69% of tasks
- Reading comprehension (StoryCloze): 80.8% vs. 78.5%
- WinRate: 70.1% vs. 64.6%
- Mathematical reasoning (GSM8K): 52.4% vs. 40.5%

**Scaling for transfer:** The optimal ratio between pre-training tokens and downstream fine-tuning examples shifts as total compute increases. With more compute, the optimal strategy uses both more pre-training data and more fine-tuning examples, with pre-training data scaling faster.

## Key Contributions

1. **(Kaplan et al.)** Universal power-law scaling for language model performance across 7 orders of magnitude, providing a principled framework for resource allocation.
2. **(Chinchilla)** Demonstration that the optimal scaling ratio is 1:1 between model parameters and training tokens (by token count), correcting Kaplan et al.'s bias toward larger models.
3. **(Chinchilla)** Empirical validation that a 70B model trained on 1.4T tokens outperforms a 280B model trained on 300B tokens at the same compute cost, proving that training longer on more data is often preferable to scaling model size.
4. Unified framework for predicting performance of models of any size trained on any dataset size with any compute budget.

## Results (Specific Numbers)

- Kaplan et al. power-law exponents: α_N ≈ 0.076, α_D ≈ 0.095, α_C ≈ 0.050
- Kaplan et al. optimal scaling: N_opt ∝ C^0.73, D_opt ∝ C^0.27
- Chinchilla optimal scaling: N_opt ∝ C^0.50, D_opt ∝ C^0.50 (tokens ∝ parameters)
- Chinchilla 70B vs. Gopher 280B (same compute ~5×10^23 FLOPs):
  - MMLU: 67.5% vs. 60.0% (+7.5 points)
  - StoryCloze: 80.8% vs. 78.5% (+2.3 points)
  - WinRate: 70.1% vs. 64.6% (+5.5 points)
  - GSM8K: 52.4% vs. 40.5% (+11.9 points)
- GPT-3 175B (Kaplan): trained on ~300B tokens (sub-optimal ratio ~0.57 tokens/param)
- Chinchilla: 1.4T tokens / 70B params = 20 tokens/param (near-optimal)
- PaLM (540B, 780B tokens): tokens/param = 1.44 (sub-optimal, following Kaplan's biased recommendation)

## Why It Matters / Impact

The Chinchilla scaling laws fundamentally changed how companies train large language models. Before Chinchilla, the field pursued ever-larger models (GPT-3 175B, PaLM 540B, Megatron-Turing 530B) with relatively little training data. After Chinchilla, the focus shifted to training smaller models much longer (Llama-2 70B on 2T tokens, Mistral 7B, Gemma 2B). This reduced the cost of inference (smaller models) while maintaining or improving quality. The scaling laws also provided benchmarks for detecting under-training: models with tokens/param < 20 are likely sub-optimal.

## Weaknesses / Limitations

1. The power-law relationships hold for average test loss but may not predict performance on specific downstream tasks, which can have different scaling behavior.
2. Chinchilla's 1:1 optimal ratio assumes a fixed compute budget and does not account for inference cost, which favors smaller models with more training data.
3. The analysis is limited to decoder-only Transformer language models; scaling behavior may differ for encoder-decoder or mixture-of-experts architectures.
4. The Kaplan et al. analysis used a single learning rate schedule that may have introduced systematic bias toward larger models (by not training long enough).
5. Real-world training involves data quality, which can vary enormously and is not captured by token count alone.

## Follow-up Work

- LLaMA (Touvron et al., 2023): Trained 7B-65B models on 1T-1.4T tokens, demonstrating Chinchilla-optimal training for open-source models.
- PaLM-2 (Anil et al., 2023): Incorporated Chinchilla insights for balanced scaling across compute budgets.
- Compute-optimal finetuning: Extended Chinchilla framework to determine optimal fine-tuning data allocation.
- Beyond Chinchilla: Studies showing that scaling beyond 1:1 ratio (more data than Chinchilla recommends) can still improve performance for practical models where inference cost matters.
