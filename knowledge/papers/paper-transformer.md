---
topic: papers
difficulty: hard
tags: [paper, transformer, attention, deep-learning, nlp]
---

# Attention Is All You Need

**Authors:** Vaswani et al. (Google Brain, Google Research, University of Toronto)
**Published:** NeurIPS 2017
**arXiv:** 1706.03762

## Problem & Motivation

Recurrent neural networks (RNNs), particularly LSTMs and GRUs, are the dominant sequence transduction models. However, they have two fundamental limitations:

1. **Sequential computation prevents parallelization** - RNNs must process tokens one at a time, making it impossible to parallelize within training examples
2. **Long-range dependencies are hard to learn** - Despite gating mechanisms, gradient flow through long sequences remains difficult, limiting performance on tasks requiring long-distance reasoning

The attention mechanism had already been shown to improve sequence modeling, but typically as an add-on to RNN architectures. This paper asks: can attention alone, without any recurrence, be sufficient for sequence transduction?

## Key Idea / Architecture

The Transformer replaces recurrence entirely with **multi-head self-attention**. The architecture has an encoder-decoder structure:

**Encoder:** Stack of N=6 identical layers, each with:
- Multi-head self-attention over input sequence
- Position-wise feed-forward network
- Residual connections and layer normalization around each sub-layer

**Decoder:** Stack of N=6 identical layers, each with:
- Masked multi-head self-attention over output sequence
- Multi-head attention over encoder output
- Position-wise feed-forward network
- Residual connections and layer normalization

### Self-Attention

The core operation computes attention weights between all positions:

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

where Q (query), K (key), V (value) are linear projections of the input.

### Multi-Head Attention

Instead of a single attention function, the model uses h parallel attention heads:

$$\text{MultiHead}(Q, K, V) = \text{Concat}(\text{head}_1, ..., \text{head}_h)W^O$$

$$\text{head}_i = \text{Attention}(QW_i^Q, KW_i^K, VW_i^V)$$

With h=8 heads and d_model=512, each head operates on d_k=64 dimensions.

### Position-wise Feed-Forward Network

$$\text{FFN}(x) = \max(0, xW_1 + b_1)W_2 + b_2$$

Applied independently to each position with inner dimension d_ff=2048.

### Positional Encoding

Since attention is permutation-equivariant, positional information is injected via sinusoidal functions:

$$PE_{(pos, 2i)} = \sin(pos / 10000^{2i/d_{model}})$$
$$PE_{(pos, 2i+1)} = \cos(pos / 10000^{2i/d_{model}})$$

## Key Contributions

1. **First entirely attention-based sequence model** - Eliminates recurrence entirely, enabling much more parallelization
2. **Multi-head attention mechanism** - Allows the model to jointly attend to information from different representation subspaces
3. **Positional encoding scheme** - Enables the model to leverage sequence order without recurrence
4. **Extensive ablation studies** - Systematic analysis of attention heads and architectural choices
5. **Significantly faster training** - 12 hours on 8 GPUs vs days/weeks for comparable RNN models

## Results

- **WMT 2014 English-German:** 28.4 BLEU, improving over existing best by >2 BLEU
- **WMT 2014 English-French:** 41.0 BLEU, a new single-model state-of-the-art
- **Training speed:** 3.5 days on 8 P100 GPUs (vs weeks for comparable models)
- Ablation confirms self-attention is faster than recurrent layers for shorter sequences, and faster than convolutional approaches for very long sequences

## Why It Matters

This paper fundamentally changed the field of deep learning. The Transformer architecture became the foundation for essentially all subsequent large language models (GPT, BERT, etc.), vision models (ViT), and multimodal systems. The key insight - that attention can replace recurrence entirely - enabled:

1. Massive parallelization leading to much larger models
2. Better modeling of long-range dependencies
3. The scaling revolution that produced GPT-3, GPT-4, and beyond

## Weaknesses

- Quadratic complexity O(N²) in sequence length limits context window
- No inherent notion of position (relies on positional encoding)
- The paper doesn't explore the limits of scaling - that came later

## Follow-up Work

- **GPT/BERT:** Applied Transformer to language modeling and understanding
- **Vision Transformer (ViT):** Applied Transformer to computer vision
- **Efficient Transformers:** FlashAttention, Linformer, etc. to address quadratic complexity
- **Scaling Laws:** Showed how to scale Transformer models effectively