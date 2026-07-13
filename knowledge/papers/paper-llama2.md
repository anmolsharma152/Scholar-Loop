---
topic: papers
difficulty: hard
last_sent:
review_count: 0
tags:
  - paper
  - llama
  - rlhf
  - open-source
  - safety
  - fine-tuning
  - chat-models
---

# Llama 2: Open Foundation and Fine-Tuned Chat Models

**Authors:** Hugo Touvron, Louis Martin, Kevin Stone, Peter Albert, Amjad Almahairi, et al. (GenAI, Meta)
**Published:** arXiv preprint, July 2023
**arXiv:** 2307.09288v2

## Problem & Motivation

Closed-source LLMs like ChatGPT, BARD, and Claude are heavily fine-tuned for human preference alignment, greatly enhancing usability and safety, but this process is not transparent or reproducible. Prior open pretrained models like LLaMA-1, BLOOM, and Falcon matched closed pretrained competitors but were not suitable substitutes for closed product LLMs. Llama 2 aims to release pretrained and fine-tuned LLMs at scales up to 70B parameters that are competitive with closed-source models on helpfulness and safety benchmarks, with a detailed description of the fine-tuning methodology to enable the community to build on the work and contribute to responsible LLM development.

## Key Idea / Architecture

### Pretraining

Llama 2 uses the standard transformer architecture with pre-normalization via RMSNorm, SwiGLU activation, and rotary positional embeddings (RoPE). Key changes from Llama 1: doubled context length (4K tokens), grouped-query attention (GQA) for 34B and 70B models for inference scalability, trained on 2T tokens (40% more than Llama 1's 1.0-1.4T tokens). AdamW optimizer with beta1=0.9, beta2=0.95, cosine learning rate schedule with 2000 warmup steps, weight decay 0.1, gradient clipping 1.0. Models were pretrained on NVIDIA A100-80GB GPUs across Meta's Research Super Cluster and production clusters.

### Fine-Tuning Pipeline (Llama 2-Chat)

The pipeline proceeds in stages: supervised fine-tuning (SFT) on ~27,540 high-quality annotations, then iterative RLHF using both rejection sampling and Proximal Policy Optimization (PPO). Two separate reward models are trained—one for helpfulness and one for safety—to address the helpfulness-safety tension. The safety reward model is trained on safety-specific annotation data. Iterative reward modeling data is accumulated in parallel with model enhancements to ensure reward models remain within distribution.

### Safety

Safety fine-tuning uses 29,000+ safety annotations across multiple risk categories. Red-teaming conducted by domain experts. The approach includes safety-specific data annotation, safety tuning, and iterative evaluation. Total pretraining carbon footprint: 539 tCO2 eq (100% offset by Meta).

## Key Contributions

1. Open release of pretrained (7B, 13B, 34B, 70B) and chat-optimized models with detailed methodology
2. Novel RLHF pipeline with dual reward models (helpfulness + safety) and iterative refinement through rejection sampling and PPO
3. Safety fine-tuning with 29,000+ safety annotations, red-teaming by domain experts, and iterative safety evaluation
4. Human evaluation results: Llama 2-Chat 70B competitive with ChatGPT on helpfulness, preferred by human raters

## Results (Specific Numbers)

### Pretrained Model Benchmarks

| Model | Code | Commonsense | World Knowledge | MATH | MMLU | BBH |
|-------|------|-------------|-----------------|------|------|-----|
| Llama 2-70B | 37.5 | 71.9 | 63.6 | 35.2 | 68.9 | 51.2 |
| Llama 1-65B | 30.7 | 70.7 | 60.5 | 30.8 | 63.4 | 43.5 |
| MPT-30B | 28.9 | 64.9 | 50.0 | 9.1 | 46.9 | 38.0 |
| Falcon-40B | 15.2 | 69.2 | 56.7 | 12.6 | 55.4 | 37.1 |

### Human Evaluation

- Helpfulness: Llama 2-Chat 70B preferred over ChatGPT in majority of ~4K prompts (95% CI: 1-2%)
- Safety: Evaluated on ~2,000 adversarial prompts
- GPT-4 as judge: win-rate analysis confirms Llama 2-Chat superiority over commercial baselines

### Training Details

- 2 trillion tokens, 4K context length, 32K BPE vocabulary
- Total GPU hours: 3,312,000 (cumulative across 7B, 13B, 34B, 70B)
- Carbon footprint: 539 tCO2 eq, 100% offset

## Why It Matters / Impact

Llama 2 democratized access to competitive chat-optimized LLMs, enabling researchers and companies to build on a strong open foundation without incurring massive pretraining costs. The detailed RLHF methodology with dual reward models became a reference implementation for safety alignment. The open release strategy shifted industry expectations around transparency and reproducibility of aligned LLMs.

## Weaknesses / Limitations

- Training data mix details not fully disclosed beyond high-level categories
- 34B model delayed due to insufficient red-teaming time
- English-only evaluation—multilingual performance not covered
- Human evaluations are noisy due to prompt set limitations and rater subjectivity
- Safety evaluations may be biased toward Llama 2-Chat models
- Still produces harmful outputs under adversarial prompting
- No benchmark numbers for the released models on standard academic benchmarks beyond the table

## Follow-up Work / Key References

- Llama 3 (2024) — extended to 8B, 70B, 405B with improved training and 8K context
- Touvron et al. (2023) Llama 1 — predecessor, 1T tokens, 2K context, no GQA
- OpenAssistant and Vicuna — community fine-tuned models on Llama base
- Dolly (Databricks) — another open commercial-use LLM release
- InstructGPT (Ouyang et al., 2022) — foundational RLHF methodology
- Chinchilla (Hoffmann et al., 2022) — compute-optimal training reference
