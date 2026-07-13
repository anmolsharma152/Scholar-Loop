---
topic: papers
difficulty: hard
last_sent:
review_count: 0
tags:
  - paper
  - scaling-laws
  - chinchilla
  - compute-optimal
  - language-model
  - training-efficiency
---

# Training Compute-Optimal Large Language Models (Chinchilla)

**Authors:** Jordan Hoffmann, Sebastian Borgeaud, Arthur Mensch, Elena Buchatskaya, Trevor Cai, Eliza Rutherford, Diego de Las Casas, Lisa Anne Hendricks, et al. (DeepMind)
**Published:** arXiv preprint March 2022 (presented at NeurIPS 2022)
**arXiv:** 2203.15556v1

## Problem & Motivation

Given a fixed FLOP budget, how should one trade off model size and the number of training tokens? Kaplan et al. (2020) showed that large models should be trained for fewer tokens and grow model size faster as compute increases (exponents: model size a=0.73, tokens b=0.27). This led to training very large models (175B-530B parameters) on relatively few tokens (~300B). However, this analysis had a critical flaw: it used a fixed learning rate schedule length for all models regardless of how many tokens they were trained on. Intermediate loss estimates for short-trained models were overestimates, causing the incorrect conclusion that model size should scale faster than data. Most recent large models trained for ~300B tokens (GPT-3 175B, Gopher 280B, Jurassic-1 178B, MT-NLG 530B) are significantly undertrained relative to their compute budget.

## Key Idea / Architecture

### Three Estimation Approaches

The authors train over 400 language models ranging from 70M to 16B+ parameters on 5B to 500B+ tokens. Three independent approaches estimate the compute-optimal frontier:

**Approach 1 (Minimum over training curves):** Fix model sizes (70M to 10B), train each for 4 different horizons spanning 16x range. Extract minimum loss per FLOP, fit power laws: N_opt proportional to C^a, D_opt proportional to C^b. Result: a=0.50, b=0.50.

**Approach 2 (IsoFLOP profiles):** Fix 9 FLOP budgets (6e18 to 3e21), vary model sizes up to 16B for each. Fit parabolas to loss vs model size curves to find minima. Fit power laws. Result: a=0.49, b=0.51.

**Approach 3 (Parametric loss function):** Model loss as L(N,D) = E + A/N^alpha + B/D^beta, where E captures entropy of natural text, A/N^alpha captures underparameterization, B/D^beta captures under-training. Fit using Huber loss (delta=10^-3) with L-BFGS. The efficient frontier follows: N_opt = G*(C/6)^(a), D_opt = G^(-1)*(C/6)^(b), where a = beta/(alpha+beta), b = alpha/(alpha+beta). Result: a=0.46, b=0.54.

All three converge on the same conclusion: model size and training tokens should scale equally with compute.

## Key Contributions

1. Demonstrates that for compute-optimal training, model size and training tokens should scale equally (both exponents ~0.50), contradicting Kaplan et al.'s a=0.73, b=0.27
2. Shows current LLMs are significantly undertrained—a 175B model should be trained on 4.2T tokens, not 300B
3. Trains Chinchilla (70B parameters, 1.4T tokens) on the same compute as Gopher (280B, 300B tokens), showing Chinchilla uniformly outperforms Gopher, GPT-3, Jurassic-1, and MT-NLG 530B
4. Provides practical compute-optimal token recommendations for any model size

## Results (Specific Numbers)

### Chinchilla vs Competitors

| Benchmark | Chinchilla 70B | Gopher 280B | GPT-3 175B | MT-NLG 530B |
|-----------|---------------|-------------|-----------|-------------|
| MMLU (5-shot) | 67.6% | 60.0% | 43.9% | — |
| BIG-bench avg | 65.1% | 54.4% | — | — |
| LAMBADA (0-shot) | 77.4% | 74.5% | 76.2% | 76.6% |
| RACE-h (few-shot) | 82.3% | 71.6% | 46.8% | — |
| RACE-m (few-shot) | 86.8% | 75.1% | 58.1% | 47.9% |
| TruthfulQA (10-shot) | 66.7% | 43.7% | — | — |
| Wikitext-103 PPL | 7.16 | 7.75 | — | — |

### Natural Questions (Closed-Book)

- Chinchilla 64-shot: 35.5% vs Gopher 28% (new closed-book SOTA)
- Chinchilla 5-shot: 31.5% vs Gopher 24.5%

### TruthfulQA

- 0-shot: Chinchilla 43.6% vs Gopher 29.5% (+14.1%)
- 10-shot: Chinchilla 66.7% vs Gopher 43.7%

### Compute-Optimal Recommendations

| Model Size | Optimal FLOPs | Optimal Tokens |
|-----------|--------------|---------------|
| 400M | 1.92e19 | 8.0B |
| 1B | 1.21e20 | 20.2B |
| 10B | 1.23e22 | 205.1B |
| 67B | 5.76e23 | 1.5T |
| 175B | 3.85e24 | 4.2T |
| 280B (Gopher) | 9.90e24 | 6.8T |

## Why It Matters / Impact

Chinchilla fundamentally changed how the industry thinks about LLM training. It proved that the prevailing strategy of making models ever-larger while keeping training data constant was wasteful—smaller models trained on more data achieve the same or better performance at the same compute budget, with lower inference cost and smaller memory footprint. This directly influenced subsequent models: Llama (Touvron et al., 2023) was trained on 1T tokens for 7B parameters. The paper created the "data wall" concern—training truly compute-optimal models would require datasets far larger than publicly available.

## Weaknesses / Limitations

- Analysis based on smoothed training loss (proxy for test loss in infinite data regime)
- Does not account for data quality differences—assumes uniform quality
- Most models in analysis below 16B parameters; extrapolation to 100B+ has uncertainty
- The parametric loss function assumes power-law relationships that may break at extreme scales
- Does not consider fine-tuning or downstream task performance directly
- Assumes dense transformers; does not directly apply to MoE architectures

## Follow-up Work / Key References

- Touvron et al. (2023) Llama — intentionally overtrained relative to Chinchilla-optimal for inference efficiency
- Kaplan et al. (2020) — original scaling laws paper that Chinchilla corrects
- Clark et al. (2022) — scaling properties of MoE language models
- Rae et al. (2021) Gopher — the 280B model that Chinchilla outperforms with 4x fewer parameters
- Sardana et al. (2023) — extended Chinchilla analysis to account for data quality
