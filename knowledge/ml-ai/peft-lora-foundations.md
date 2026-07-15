---
topic: ml-ai
difficulty: medium
tags: [finetuning, peft, lora]
last_sent:
review_count: 0
---

# PEFT & LoRA: Foundations

## Motivation
Full fine-tuning of large language models is expensive: GPT-3 175B requires over 1.2 TB of GPU memory. Parameter-Efficient Fine-Tuning (PEFT) methods update only a small fraction of the parameters while maintaining performance within 1-2% of full fine-tuning.

## LoRA (Low-Rank Adaptation)

**Core idea:** The change in weight matrices during fine-tuning has low intrinsic rank. Instead of updating W ∈ ℝ^{d×k}, learn a low-rank decomposition ΔW = BA where B ∈ ℝ^{d×r}, A ∈ ℝ^{r×k}, and r ≪ min(d, k).

**Forward pass:** h = W₀x + BAx (the original weights are frozen; only A and B are trained)

**Rank selection:** r = 4, 8, or 16 is typical, reducing parameter count by 10,000× for 100K×100K matrices. Higher rank captures more task-specific adaptation but costs more. In practice, r=8 is a good default for most tasks.

**Scaling factor:** Output is scaled by α/r where α is a hyperparameter (default α=16 for r=8). Scaling prevents large updates to the pretrained weights.

**Where to apply:** LoRA is applied to attention projection matrices (Q, K, V, O). It can also be applied to FFN layers but typically with smaller gains.

## Key Properties
- **No inference overhead:** Once trained, W₀ + BA can be merged into a single weight matrix
- **No additional latency:** The merged model has the same structure as the base model
- **Swappable adapters:** Multiple task-specific LoRA modules can be stored and swapped at runtime (e.g., task A adapter → task B adapter)
- **Memory efficient:** Reduces trainable parameters by 10,000× vs full fine-tuning

## Adapter Methods

Before LoRA, adapters inserted bottleneck layers (down-projection → non-linearity → up-projection) between Transformer layers. Down-projection: ℝ^{d×dⁱⁿ} to ℝ^{d×r} where r ≪ d, up-projection back to ℝ^{d×dⁱⁿ}. Adapters add inference latency since they cannot be merged.
