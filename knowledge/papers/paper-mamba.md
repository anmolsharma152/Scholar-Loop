---
topic: papers
difficulty: hard
tags: [paper, mamba, state-space-models, sequence-modeling, linear-complexity]
---

# Mamba: Linear-Time Sequence Modeling with Selective State Spaces

**Authors:** Gu & Dao (Carnegie Mellon University, Princeton)
**Published:** 2023
**arXiv:** 2312.00752

## Problem & Motivation

Transformers achieve great performance but have quadratic complexity O(N²) in sequence length, limiting context window size. State-space models (SSMs) like S4 offer linear complexity but are limited by:

1. **Time-invariant dynamics** - Same parameters applied at every step, regardless of input
2. **Poor content-based reasoning** - Can't selectively focus on or ignore inputs based on content
3. **Limited expressiveness** - Fixed linear recurrences can't implement content-aware reasoning

The question: can we build a sequence model that is both linear in complexity AND selective like attention?

## Key Idea / Architecture

### Selective State Spaces

Mamba introduces input-dependent (selective) state space models. The core recurrence is:

$$h_t = \bar{A} h_{t-1} + \bar{B} x_t$$
$$y_t = C h_t$$

where $\bar{A}$, $\bar{B}$ are functions of the input $x_t$ (this is the key innovation):

$$\bar{A}_t = \exp(\Delta_t A)$$
$$\bar{B}_t = (\Delta_t A)^{-1}(\exp(\Delta_t A) - I) \cdot \Delta_t B$$

and $\Delta_t = \text{softplus}(\text{Linear}_\Delta(x_t))$ is input-dependent.

### Hardware-Aware Algorithm

The selective mechanism requires computing different recurrences for different inputs, which doesn't work with standard parallel scan. Mamba uses:

1. **Parallel associative scan** - Efficient parallel computation of recurrences
2. **GPU-aware memory hierarchy** - Fuse all operations into a single kernel
3. **SRAM optimization** - Compute in fast SRAM, avoid HBM round-trips

### Architecture

Mamba is a simple block with:
- Linear projection to expand dimensions
- 1D convolution (optional, short kernel)
- Selective SSM
- Gated output projection

Stack these blocks with residual connections and normalization to build the model.

## Key Contributions

1. **Selective SSM** - First input-dependent state space model with content-based reasoning
2. **Hardware-aware algorithm** - Makes selective SSMs practical on modern GPUs
3. **Linear scaling** - Inference and training scale linearly with sequence length
4. **Competitive performance** - Matches Transformer quality on language modeling

## Results

- **Language modeling:** Mamba-3B matches Transformer-3B perplexity while being 5x faster at generation
- **Inference throughput:** 5x higher than Transformer of similar size
- **Long-context:** Can handle sequences up to 1M tokens (vs 8K-32K for Transformers)
- **Genomics:** State-of-the-art on genome modeling benchmarks
- **Audio:** Competitive on audio generation tasks

### Scaling

- **Mamba-130M:** Competitive with Transformer-125M
- **Mamba-370M:** Competitive with Transformer-350M
- **Mamba-1.4B:** Matches Transformer-1.3B
- **Mamba-2.8B:** Competitive with Transformer-2.8B
- **Mamba-7B:** Competitive with Transformer-7B (at 5x throughput)

## Why It Matters

Mamba demonstrated that:

1. **SSMs can match Transformers** - Linear complexity doesn't mean worse performance
2. **Selectivity is the key ingredient** - Input-dependent dynamics enable content-based reasoning
3. **Hardware-algorithm co-design** - Theoretical algorithms need hardware awareness to be practical
4. **Alternative to attention** - Not all sequence modeling needs quadratic attention

## Weaknesses

- **Training instability** - SSMs can be harder to train than Transformers
- **Limited parallelism** - Recurrence limits some forms of parallel training
- **No direct interpretability** - Harder to understand than attention patterns
- **Still catching up on some tasks** - Transformers may still be better for certain reasoning tasks

## Follow-up Work

- **Mamba-2:** Improved architecture and training
- **Jamba:** Hybrid Transformer-Mamba architecture
- **SSM-Transformer hybrids:** Combining strengths of both approaches
- **Application-specific variants:** Mamba for vision, code, etc.