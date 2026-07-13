---
topic: papers
difficulty: hard
last_sent:
review_count: 0
tags:
  - paper
  - dense-vs-moe
  - mixture-of-experts
  - efficiency
  - reasoning
  - prompting
---

# Gemma 4, Phi-4, and Qwen3: Accuracy-Efficiency Tradeoffs in Dense and MoE Reasoning Language Models

**Authors:** Md Motaleb Hossen Manik, Ge Wang (Rensselaer Polytechnic Institute)
**Published:** arXiv preprint April 2026
**arXiv:** 2604.07035v1

## Problem & Motivation

Practitioners deploying LLMs face a practical choice: smaller dense models, larger dense models, or sparsely-activated mixture-of-experts (MoE) models whose total parameter counts are large but active compute per token is much smaller. Latency, throughput, and GPU memory often determine what can actually be served, yet comparison literature still centers capability in isolation or reports efficiency under heterogeneous evaluation setups. Prompting strategy has become a first-class variable—a model strong under zero-shot prompting may not remain strongest under chain-of-thought. This paper fills the gap with a controlled deployment-aware comparison across seven open-weight models, three prompting regimes, and four reasoning benchmarks under unified hardware, decoding pipeline, and evaluation protocol.

## Key Idea / Architecture

### Controlled Empirical Benchmark

The study evaluates seven open-weight reasoning-oriented models in a full-factorial design: Model x Task x Prompting Strategy, with 100 examples per condition yielding 7 x 4 x 3 x 100 = 8,400 total scored examples. All models are evaluated on the same server with a unified inference pipeline, common decoding settings, and the same sample sizes.

### Models Evaluated

The seven models span both dense and MoE architectures at various scales. Dense models include Phi-4-mini-reasoning (3.8B parameters, 3.8B active), Qwen3-8B (8B parameters, 8B active), and Phi-4-reasoning (14B parameters, 14B active). MoE models include Gemma-4-E2B (5B total, 2B active), Gemma-4-E4B (8B total, 4B active), Qwen3-30B-A3B (30B total, 3B active), and Gemma-4-26B-A4B (26B total, ~4B active).

### Benchmarks and Prompting

Four benchmarks span science reasoning (ARC-Challenge), grade-school math (GSM8K), harder mathematics (Math Level 1-3), and truthfulness (TruthfulQA MC1). Three prompting strategies are tested: zero-shot, chain-of-thought (CoT), and few-shot chain-of-thought with worked examples.

### Evaluation Metrics

Metrics include accuracy, latency, peak GPU memory (VRAM), output length, tokens/second, and approximate FLOPs-per-token. The framework jointly reports a prompt-conditioned Pareto frontier over accuracy, latency, memory, and compute cost. Statistical analyses include confidence intervals, pairwise significance tests, and weighted cross-task summaries.

## Key Contributions

1. Controlled benchmark of seven open-weight dense and MoE models under a unified inference and evaluation setup, enabling direct comparison across architectures and scales
2. Prompt-conditioned Pareto analysis framework jointly reporting accuracy, latency, memory, output length, and compute cost, revealing tradeoffs hidden by accuracy-only comparisons
3. Cross-task, cross-prompt analysis showing model rankings are unstable across prompting regimes and benchmark families, with mid-scale sparse models occupying especially favorable deployment frontiers
4. Release of a fully reproducible evaluation pipeline with aggregated result tables, pairwise significance analyses, and figure-generation scripts

## Results (Specific Numbers)

### Weighted Multi-Task Summary

| Rank | Model | Strategy | Weighted Acc. | VRAM (GB) | Latency (s) |
|------|-------|----------|--------------|-----------|-------------|
| 1 | Gemma-4-E4B | Few-shot CoT | 0.675 | 14.89 | 5.46 |
| 2 | Gemma-4-26B-A4B | Few-shot CoT | 0.663 | 48.07 | 8.04 |
| 3 | Gemma-4-E4B | Zero-shot | 0.509 | 14.89 | 7.22 |
| 4 | Gemma-4-E2B | Few-shot CoT | 0.493 | 9.54 | 4.91 |

### Task-Specific Best Models

- **ARC-Challenge**: Gemma-4-26B-A4B, 0.960 accuracy
- **GSM8K**: Gemma-4-26B-A4B (few-shot CoT), 0.680; Phi-4-reasoning CoT: 0.670
- **Math Level 1-3**: Gemma-4-E4B (few-shot CoT), 0.490
- **TruthfulQA**: Phi-4-reasoning (few-shot CoT), 1.000 (perfect)

### Largest Prompting Effects

- Phi-4-reasoning on GSM8K collapsed from 0.67 (CoT) to 0.11 (few-shot CoT), a spread of 0.560
- Gemma-4-26B-A4B on GSM8K: 0.680 (few-shot CoT) vs 0.280 (CoT), spread 0.400
- Qwen3-8B on GSM8K: 0.280 (few-shot CoT) vs 0.010 (zero-shot), spread 0.270

### Efficiency Observations

- Qwen3-30B-A3B had lowest FLOPs/token (6.0e9) but weighted accuracy only 0.226—sparse activation alone did not translate to strong performance
- Gemma-4-E4B achieved highest accuracy at moderate FLOPs with 14.9 GB VRAM

## Why It Matters / Impact

This paper demonstrates that sparse MoE activation alone does not guarantee the best practical operating point. The accuracy-efficiency tradeoff depends jointly on architecture, prompting protocol, and task composition. Mid-sized MoE models like Gemma-4-E4B occupy especially favorable deployment frontiers, achieving better accuracy than larger models at a fraction of the memory cost. It argues against one-dimensional leaderboard interpretation and in favor of multi-objective operating points.

## Weaknesses / Limitations

- Only 7 models evaluated, all English-only; no multilingual benchmarks
- 100 examples per model-dataset-strategy condition may not capture the full distribution
- FLOPs are approximate based on model metadata, not measured on hardware
- Fixed hardware setup (single GPU); results may vary across different GPUs and inference engines
- Does not test quantized or distillation variants that practitioners often deploy

## Follow-up Work / Key References

- Kaplan et al. (2020) - foundational scaling laws that this work builds upon for efficiency analysis
- Hoffmann et al. (2022) Chinchilla - compute-optimal training, referenced for MoE scaling context
- Touvron et al. Llama 2 - open-weight model family compared in related work
- Reproducible benchmark pipeline released at: https://github.com/mkboch/dense_and_moe_reasoning
- Holistic Evaluation of Language Models (HELM) - multi-metric evaluation framework referenced
