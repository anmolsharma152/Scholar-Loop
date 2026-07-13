---
topic: papers
difficulty: hard
last_sent:
review_count: 0
tags:
  - paper
  - gemini
  - multimodal
  - large-language-model
  - safety
  - nano
  - tpu
---

# Gemini: A Family of Highly Capable Multimodal Models

**Authors:** Gemini Team, Google
**Published:** arXiv preprint, updated May 2025
**arXiv:** 2312.11805v5

## Problem & Motivation

Prior multimodal models either excelled at language or vision/audio, not both simultaneously. No existing model matched human-level reasoning across text, images, audio, and video. The field needed natively multimodal training—jointly training on all modalities from scratch rather than post-hoc alignment of separate encoders. The goal was to build a model family spanning from complex reasoning tasks (Ultra) to on-device deployment (Nano), advancing state-of-the-art across all 32 benchmarks evaluated.

## Key Idea / Architecture

### Natively Multimodal from Training

Gemini models are trained jointly on text, images, audio, and video from scratch, unlike post-hoc vision-language alignment approaches (e.g., Flamingo's late fusion). This allows the model to learn cross-modal reasoning naturally. Visual encoding is inspired by Flamingo, CoCa, and PaLI, but with the distinction that models can natively output images using discrete image tokens.

### Model Sizes

Gemini 1.0 comes in three sizes: Ultra (most capable, complex reasoning tasks), Pro (performance-optimized, deployable at scale), and Nano (on-device, with two versions: Nano-1 at 1.8B parameters for low-memory devices and Nano-2 at 3.25B for high-memory devices, both 4-bit quantized and trained via distillation from larger Gemini models).

### Training Infrastructure

Training used TPUv5e and TPUv4 accelerators. Ultra trained on a large fleet of TPUv4s across multiple datacenters in SuperPods of 4096 chips connected via optical switches, achieving 97% goodput through redundant in-memory model state copies. The JAX/Pathways single-controller programming model orchestrated training. Google's intra-cluster and inter-cluster networking enabled synchronous training with model parallelism within superpods and data parallelism across superpods. SentencePiece tokenizer trained on a large sample of the entire corpus.

## Key Contributions

1. State-of-the-art in 30 of 32 benchmarks; first model to exceed human expert performance on MMLU at 90.04%
2. Natively multimodal from training: jointly processes text, images, audio, video with cross-modal reasoning
3. On-device deployment via Nano models (1.8B/3.25B) with 4-bit quantization, distilled from larger models
4. AlphaCode 2 powered by Gemini: ranks top 15% on Codeforces competitive programming (vs top 50% for predecessor)
5. TPU infrastructure innovations: 97% goodput, inter-datacenter training, deterministic replay for SDC detection

## Results (Specific Numbers)

### Text and Reasoning

- **MMLU**: Gemini Ultra 90.04% (first to exceed human expert 89.8%); prior SOTA GPT-4 86.4%
- **GSM8K** (grade-school math, CoT + self-consistency): Gemini Ultra 94.4%; prior best 92%
- **MATH** (competition math, 4-shot): Gemini Ultra 53.2%; GPT-4 42.5%
- **HumanEval** (code): Gemini Ultra 74.4%; GPT-4 67%
- **Natural2Code** (held-out Python, no web leakage): Gemini Ultra 74.9%
- **AMC 10/12 2022-2023**: Gemini Ultra 32% vs GPT-4 30%

### Multimodal

- **MMMU** (multimodal reasoning): Gemini Ultra 62.4%; prior best 56.8%
- **HellaSwag** (10-shot decontaminated): Gemini Ultra 85.9%, Pro 84.0%
- **Needle-in-a-haystack**: 99.7% recall at 100K tokens

### Audio

- **LibriSpeech ASR**: Gemini Ultra 4.7% WER vs Whisper 5.5%

### Benchmark Coverage

- 10 of 12 text/reasoning benchmarks SOTA
- 9 of 9 image understanding benchmarks SOTA
- 6 of 6 video understanding benchmarks SOTA
- 5 of 5 speech recognition/translation benchmarks SOTA

## Why It Matters / Impact

Gemini established that natively multimodal training from scratch outperforms post-hoc alignment approaches. The MMLU milestone (first to beat human experts) demonstrated frontier capability. Nano models proved on-device deployment is viable with distilled, quantized versions retaining strong performance. The TPU infrastructure innovations (97% goodput, inter-datacenter training) pushed the boundary of large-scale training systems. The report also provided the first public details on training infrastructure at this scale.

## Weaknesses / Limitations

- Architecture details not fully disclosed (model sizes for Ultra and Pro not published)
- Many benchmarks may have contamination issues despite decontamination efforts
- HellaSwag results sensitive to pretraining data composition (100 fine-tuning steps improved Pro to 89.6%)
- Nano models have limited capability on complex reasoning tasks
- Not open-source, limiting reproducibility and community adaptation
- Image generation capability limited compared to dedicated generative models
- Evaluation relies heavily on benchmark numbers that may not reflect real-world performance

## Follow-up Work / Key References

- Gemini 1.5 (2024) — extended context to 1M+ tokens with MoE architecture
- Gemini 2.0 (2024) — agentic capabilities
- PaLM 2 (Anil et al., 2023) — predecessor, Gemini Ultra outperforms across most benchmarks
- AlphaCode 2 (Leblond et al., 2023) — competitive programming agent powered by Gemini
- Hoffmann et al. (2022) Chinchilla — compute-optimal training principles applied to token counts
- Vaswani et al. (2017) Transformer — foundational architecture
