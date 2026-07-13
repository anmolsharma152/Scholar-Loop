---
difficulty: hard
last_sent: 2026-07-13 23:24:09.627288+00:00
review_count: 1
tags:
- paper
- peft
- fine-tuning
- lora
- adapters
- survey
topic: papers
---

# Parameter-Efficient Fine-Tuning for Large Models: A Comprehensive Survey

**Authors:** Zeyu Han, Chao Gao, Jinyang Liu, Jeff (Jun) Zhang, Sai Qian Zhang (Northeastern, UC Riverside, ASU, NYU)
**Published:** arXiv 2024
**arXiv:** 2403.14608

## Problem & Motivation

Large language models with billions of parameters (e.g., GPT-3 at 175B, LLaMA-7B) achieve remarkable performance but are computationally expensive to fine-tune for downstream tasks. Standard full fine-tuning requires adjusting all parameters, demanding thousands of GPUs working in parallel—making it unsustainable and inaccessible for resource-constrained settings. The field needed a systematic taxonomy and evaluation of Parameter-Efficient Fine-Tuning (PEFT) methods that selectively adjust a small fraction of parameters while keeping the rest frozen, balancing performance with computational cost.

## Key Idea / Architecture

PEFT methods are categorized into four families based on their computational flow:

**Additive PEFT** introduces new trainable modules or parameters while keeping the backbone frozen:
- *Adapters*: Small bottleneck layers (down-project → nonlinear → up-project) inserted after self-attention and FFN layers. An adapter with bottleneck dimension r computes: Adapter(x) = W_up · σ(W_down · x) + x. Serial adapters (Houlsby et al., 2019) insert two per Transformer block; parallel adapters (He et al., 2021) run alongside sublayers. CoDA uses sparse activation, processing only top-k tokens through the frozen layer.
- *Soft Prompt Tuning*: Learnable vectors prepended to input sequences. Prefix-tuning (Li & Liang, 2021) adds learnable keys/values across all layers with MLP reparameterization. Prompt-tuning (Lester et al., 2021) adds vectors only at the input embedding layer—effective primarily for models >11B parameters. p-tuning v2 removes reparameterization and scales to broader settings.

**Selective PEFT** fine-tunes a subset of existing parameters via binary masking:
- Unstructured: Diff pruning (l0-norm regularization), FishMask (Fisher information), PaFi (smallest magnitude selection), Child-tuning.
- Structural: Grouping weights into nodes/rows and selecting entire structures (FAR, BitFit for bias-only tuning, SPT for sensitivity-aware selection).

**Reparameterized PEFT** constructs low-rank trainable matrices during training, merged back for inference:
- *LoRA* (Hu et al., 2021): Adds ΔW = α/r · W_up · W_down to pretrained weight W0, where W_up ∈ R^{d×r}, W_down ∈ R^{r×k}, r ≪ min(d,k). At training start, W_down is random Gaussian, W_up is zero. Evaluated on models up to 175B parameters.
- DyLoRA trains across a range of ranks simultaneously. AdaLoRA uses SVD with importance-based pruning. SoRA adds a gating unit between W_up and W_down.
- DoRA decomposes weights into magnitude (m) and direction (V), applying LoRA only to V: W' = m · (V + ΔV)/||V + ΔV||.
- VeRA shares frozen random low-rank matrices across all layers, learning only small scaling vectors (orders of magnitude fewer parameters than LoRA).

**Hybrid PEFT** combines methods: UniPELT integrates LoRA + prefix + adapters with gating; MAM Adapter combines adapter, prefix, and BitFit across layer groups.

The survey also covers system-level optimizations: KV-cache management for PEFT efficiency, PEFT pruning, quantization, and memory-efficient training. It examines applications across LLMs, Vision Transformers, vision-language alignment models, and diffusion models.

## Key Contributions

1. Comprehensive taxonomy of PEFT algorithms into additive, selective, reparameterized, and hybrid categories with mathematical formulations for each.
2. Analysis of system-level costs: compute overhead, memory footprint, and inference latency for different PEFT methods.
3. Survey of applications across NLP (GLUE, SuperGLUE, commonsense reasoning), computer vision (FGVC, VTAB, MSCOCO, ADE20K), vision-language models, and diffusion models.
4. Discussion of system design challenges: centralized PEFT serving, distributed PEFT training, and parallel PEFT training systems.

## Results (Specific Numbers)

- LoRA on RoBERTa-large: GLUE avg 87.5% with only 0.8% trainable parameters vs. 93.5M full fine-tuning parameters
- Adapter on RoBERTa-large (bottleneck r=64): ~86.5 GLUE with ~3.6% parameters
- (IA)3 adds only 3 rescaling vectors per layer (~0.01% of total parameters)
- Prompt-tuning effectiveness: negligible gap with full fine-tuning for models >11B parameters
- VeRA: comparable to LoRA with orders of magnitude fewer parameters (e.g., 0.013% vs. 0.52% on RoBERTa-large)
- Full fine-tuning of LLaMA-7B requires thousands of GPUs; PEFT reduces this to a single GPU

## Why It Matters / Impact

PEFT democratizes access to large model customization by reducing fine-tuning costs from thousands of GPUs to a single consumer GPU. It enables serving multiple task-specific adapters from a single frozen backbone, critical for multi-tenant deployment. The taxonomy provides a principled framework for selecting PEFT methods based on compute budget, model size, and task requirements. These methods have become standard practice in production LLM deployment.

## Weaknesses / Limitations

1. Many PEFT methods are evaluated primarily on GLUE-scale benchmarks; performance on more complex or generative tasks remains less explored.
2. The optimal choice of rank (LoRA), bottleneck dimension (adapters), or number of prompt tokens is task-dependent and requires tuning.
3. Combination of PEFT methods (hybrid) increases design space complexity without clear automated selection strategies.
4. System-level analysis shows significant implementation-dependent variation in actual speedups, making fair comparison challenging.
5. Most analysis focuses on encoder or encoder-decoder models; decoder-only LLM PEFT behavior is less thoroughly characterized.

## Follow-up Work

- QLoRA (Dettmers et al., 2023): Combines LoRA with 4-bit quantization for fine-tuning 65B models on a single 48GB GPU.
- LoRA+ (Hayou et al., 2024): Different learning rates for W_up and W_down matrices.
- DoRA (Liu et al., 2024): Weight-decomposed LoRA consistently outperforming standard LoRA.
- AdaLoRA (Zhang et al., 2023): Adaptive rank allocation via SVD importance scoring.