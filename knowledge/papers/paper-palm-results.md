---
topic: papers
difficulty: hard
tags: [paper, palm, llm, results]
last_sent:
review_count: 0
---

# PaLM: Results & Breakthroughs

## Few-Shot Results

PaLM set new state-of-the-art across many benchmarks:

| Benchmark | PaLM 540B | Few-shot SOTA before PaLM |
|---|---|---|
| MMLU | 69.3% | 57.0% (Gopher 280B) |
| BIG-Bench | 61.4 average | 43.0 (Gopher) |
| GSM8K | 58% (8-shot) | 17.9% (code-davinci-002) |
| HumanEval | 26.2% (97.4% before filtering) | 23.7% (code-davinci-002) |

**Breakthrough performance on BIG-Bench:** PaLM solved tasks that previous models could not, including logical deduction (88.9%), causal judgment (76.7%), and date understanding (99.1%).

**Chain-of-thought scaling:** CoT prompting improved GSM8K from 17.9% → 58%, demonstrating that scaling to 540B unlocks reasoning capabilities that are not linearly scaling with other metrics.

## Multi-lingual Performance

PaLM performed well on translation (BLEU: 34.3 En→Fr, 24.0 En→Zh) and cross-lingual NLU tasks from XTREME (XNLI accuracy: 79.8%), despite being primarily English-pretrained (6.7% non-English in training).

## Discontinuity in Scaling Behavior

PaLM showed "breakthrough" behavior where some capabilities emerge suddenly around 100-200B parameters:

- Correcting multi-step reasoning errors
- Recognizing word-in-category (e.g., "Is Wednesday a bird?")
- Mathematical problem solving with worked examples

This suggests that scaling reveals qualitative breakthroughs rather than smooth improvements — the key motivation for pushing to very large model sizes.

## Weaknesses

1. Safety evaluation was limited; the model showed socio-economic biases
2. Zero-shot translation was weaker than dedicated NMT models
3. The scale required 6144 TPUv4 chips — inaccessible to most researchers
4. The 780B token pretraining was later found to be suboptimal (Chinchilla would say 540B model needs ~5T tokens)

**Contrast to Chinchilla:** PaLM was trained on ~1.4 tokens/param (780B tokens / 540B params). Chinchilla suggests ~20 tokens/param for compute-optimal training. PaLM was likely under-trained.
