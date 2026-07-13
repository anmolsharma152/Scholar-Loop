---
topic: papers
difficulty: hard
tags: [paper, lora, parameter-efficient-fine-tuning, adapters, low-rank]
---

# LoRA: Low-Rank Adaptation of Large Language Models

**Authors:** Hu et al. (Microsoft Research)
**Published:** ICLR 2022
**arXiv:** 2106.09685

## Problem & Motivation

Fine-tuning large language models is computationally expensive:
- Full fine-tuning requires updating all parameters (e.g., 175B for GPT-3)
- Training separate copies of the model for each task is wasteful
- Gradient-based fine-tuning requires storing optimizer states for all parameters

The question: can we fine-tune models by updating only a small number of parameters?

## Key Idea / Architecture

### Low-Rank Decomposition

The key insight: during fine-tuning, weight updates have a low "intrinsic dimensionality". For a pre-trained weight matrix $W_0 \in \mathbb{R}^{d \times k}$, we can parameterize the update as:

$$W = W_0 + \Delta W = W_0 + BA$$

where $B \in \mathbb{R}^{d \times r}$ and $A \in \mathbb{R}^{r \times k}$, with $r \ll \min(d, k)$.

### How LoRA Works

1. Freeze pre-trained weights $W_0$
2. Add trainable low-rank matrices $A$ and $B$
3. Only train $A$ and $B$ during fine-tuning
4. No change in inference latency (can merge $W = W_0 + BA$)

### Initialization

- $A$ is initialized with Gaussian random values
- $B$ is initialized to zeros
- This ensures $\Delta W = BA = 0$ at the start of training
- A scaling factor $\alpha/r$ is applied: $\Delta W = \frac{\alpha}{r} BA$

### Where to Apply LoRA

LoRA is applied to attention layers ($W_Q, W_K, W_V, W_O$) in Transformers. The paper finds:
- Applying to $W_Q$ and $W_V$ gives best results
- Rank $r = 4$ or $r = 8$ works well in practice
- Higher ranks don't necessarily improve performance

## Key Contributions

1. **Parameter-efficient fine-tuning** - Update only 0.1-1% of parameters
2. **No inference overhead** - Merged weights have same size as original
3. **Better than full fine-tuning** - LoRA often outperforms full fine-tuning
4. **Task-specific adapters** - Small per-task weights can be swapped efficiently

## Results

- **RoBERTa:** LoRA achieves 24.0 on GLUE vs 24.2 for full fine-tuning (with 10,000x fewer parameters)
- **GPT-3 175B:** LoRA matches full fine-tuning on NLU benchmarks
- **Inference speed:** Same as original model (no overhead)
- **Memory:** ~40% reduction in training memory vs full fine-tuning
- **Multi-task:** Can store multiple adapters efficiently and swap at runtime

### Key Observations

1. **Low ranks are sufficient** - Rank 4-8 works as well as higher ranks
2. **More LoRA modules help** - Applying to more weight matrices improves performance
3. **Initialization matters** - Zero initialization of B is crucial
4. **Hyperparameter sensitivity** - Learning rate needs adjustment vs full fine-tuning

## Why It Matters

LoRA became one of the most widely used fine-tuning methods:

1. **Democratized fine-tuning** - Made large model fine-tuning accessible
2. **Commercial viability** - Enables serving multiple tasks with minimal memory
3. **Inspired variants** - Led to QLoRA, DoRA, and other efficient methods
4. **Standard practice** - Now used in most fine-tuning pipelines

## Weaknesses

- **Rank selection** - Optimal rank varies by task and model
- **Not universal** - Some tasks may benefit from higher-rank updates
- **Limited theoretical understanding** - Why low-rank works is not fully understood
- **Interaction with other techniques** - How LoRA interacts with other methods (quantization, pruning) is complex

## Follow-up Work

- **QLoRA:** Combines LoRA with 4-bit quantization for even more memory efficiency
- **DoRA:** Weight decomposition for better adaptation
- **AdaLoRA:** Adaptive rank allocation across layers
- **LoRA+:** Improved learning rate schedules for LoRA