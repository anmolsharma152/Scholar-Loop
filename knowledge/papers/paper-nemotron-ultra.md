---
topic: papers
difficulty: hard
last_sent:
review_count: 0
tags:
  - paper
  - mixture-of-experts
  - hybrid-architecture
  - nvidia
  - agentic
---

# Nemotron 3 Ultra: Open, Efficient Mixture-of-Experts Hybrid Mamba-Transformer Model for Agentic Reasoning

**Authors:** NVIDIA (NVIDIA Research)
**Published:** arXiv June 2026
**arXiv:** N/A

## Problem & Motivation

As LLM applications evolve from simple chatbots to long-running autonomous agents, delivering fast and efficient inference becomes increasingly critical. Existing large open-source models face an accuracy-throughput tradeoff: high-accuracy models are slow, while efficient models sacrifice capability. The authors wanted to build a model that achieves on-par accuracy with state-of-the-art public LLMs while delivering dramatically higher inference throughput—specifically optimized for long-running agentic tasks requiring tool use, code generation, and reasoning over extended contexts up to 1M tokens. The key insight is that for agentic systems, inference throughput is as important as accuracy. Models like GLM-5.1-754B and Kimi-K2.6-1T offer high accuracy but suffer from prohibitive latency.

## Key Idea / Architecture

Nemotron 3 Ultra is a 550 billion total / 55 billion active parameter Mixture-of-Experts Hybrid Mamba-Attention language model. The architecture combines three key innovations: LatentMoE for better accuracy per active parameter than standard granular MoEs, a hybrid Mamba-Attention architecture that reduces attention cost and KV cache footprint for improved throughput, and Multi-Token Prediction (MTP) heads for inference acceleration via speculative decoding.

The model has 108 total layers with 8192 model dimension. MoE layers use 512 total experts per layer with top-22 routing and a latent size of 2048. The hybrid pattern alternates between Mamba-2 layers and Attention layers (roughly every 3rd layer is attention), with GQA attention using 64 query heads and 2 KV heads. The base model was pretrained on 20 trillion text tokens using NVFP4 (E2M1 datatype with 2D block quantization), divided into two phases: 15T tokens for diversity and broad coverage, followed by 5T tokens of high-quality data for refinement.

Post-training uses a pipeline of SFT, unified RLVR across reasoning/agentic/code/safety environments, and Multi-teacher On-Policy Distillation (MOPD) consolidating 10+ domain-specialized teacher models through dense token-level guidance on student-generated rollouts. Reasoning budget control enables inference-time adjustment of the accuracy-compute tradeoff.

```
Throughput advantage: 5.9x over GLM-5.1-754B, 4.8x over Kimi-K2.6-1T, 1.6x over Qwen-3.5-397B
NVFP4 relative loss gap: <0.4% vs BF16 at 5T, 10T, and 16T checkpoints
```

## Key Contributions

1. Achieved up to 5.9x higher inference throughput than comparable frontier models while maintaining on-par accuracy across reasoning and agentic benchmarks
2. Demonstrated stable and accurate training at the largest scale to date using NVFP4 (E2M1) precision, with less than 0.4% relative loss gap vs. BF16
3. Introduced LatentMoE, achieving better accuracy per parameter than standard granular MoEs with 512 experts per layer and top-22 routing
4. Open-sourced base, post-trained, and quantized checkpoints along with training data and recipes on HuggingFace
5. Equipped the model with reasoning effort control for inference-time accuracy-compute tradeoff
6. Pretrained on 20 trillion tokens in two phases: 15T for diversity and broad coverage, 5T of high-quality data for refinement

## Results (Specific Numbers)

- SWE-Bench Verified: N3 Ultra BF16 72.4% (vs. Kimi-K2.6 69.7%, Qwen-3.5 70.9%)
- Terminal Bench 2.1: N3 Ultra BF16 56.4% (vs. Kimi-K2.6 53.0%)
- PinchBench: N3 Ultra BF16 71.9% (vs. Qwen-3.5 69.7%)
- GDPVal: N3 Ultra BF16 97.5% (vs. Kimi-K2.6 95.0%)
- IOI 2025: N3 Ultra BF16 86.6% (vs. Kimi-K2.6 81.2%)
- RULER @ 1M: N3 Ultra BF16 56.4% (vs. Kimi-K2.6 46.0%)
- Inference throughput: 5.9x GLM-5.1-754B, 4.8x Kimi-K2.6-1T, 1.6x Qwen-3.5-397B on 8K/64K setting
- LegalBench proxy accuracy improved from 64.6 to 74.7 with legal-specific pretraining data

## Why It Matters / Impact

Nemotron 3 Ultra demonstrates that hybrid Mamba-Attention MoE architectures can achieve frontier-level accuracy with dramatically better throughput, making long-running autonomous agents economically viable. The 1M token context length is particularly significant for agentic tasks requiring extensive repository context. Open-sourcing the full training recipe, data, and checkpoints enables the community to build efficient reasoning models without requiring massive proprietary infrastructure. The NVFP4 training at this scale validates low-precision training for future models. The combination of Mamba's efficient sequence modeling with sparse MoE routing creates a new architectural template for scaling inference efficiency alongside capability, with implications for both cloud deployment and edge inference.

## Weaknesses / Limitations

- 550B total parameters still require substantial infrastructure for deployment despite only 55B active per token
- The hybrid Mamba-Attention architecture adds complexity compared to pure Transformer models and may have different failure modes
- Performance on non-coding/non-reasoning tasks is less thoroughly evaluated in the report
- NVFP4 training requires specialized hardware (H100/H200 GPUs with FP4 support), limiting accessibility
- The LatentMoE with 512 experts per layer increases memory footprint even with sparse activation (top-22 routing)
- Training instabilities were observed and required careful intervention at specific token counts (5T, 10T, 16T)
- Throughput comparisons use different serving frameworks (TRT-LLM for N3 Ultra vs. vLLM for competitors), potentially introducing benchmarking bias
- The 108-layer architecture with alternating Mamba-2 and attention layers requires careful layer placement optimization

## Follow-up Work

- Integration with NVIDIA's TensorRT-LLM for optimized inference pipelines
- Extension of the hybrid Mamba-Attention architecture to multimodal models
- Scaling LatentMoE to even larger expert counts with finer-grained routing
- Application to specialized domains: legal, medical, and scientific research agents
- Exploration of latent-space expert routing for vision and multimodal understanding

---
