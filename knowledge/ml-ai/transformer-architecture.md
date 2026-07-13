---
difficulty: hard
last_sent: null
review_count: 0
tags:
- transformer
- attention
- architecture
topic: ml-ai
---

# Transformer Architecture

The Transformer is the backbone of modern NLP and increasingly vision and multimodal systems. Introduced in "Attention Is All You Need" (Vaswani et al., 2017), it replaced recurrence and convolutions entirely with **self-attention** mechanisms. The architecture comes in three variants: encoder-only (BERT), decoder-only (GPT), and encoder-decoder (original Transformer for seq2seq tasks).

## Encoder-Decoder Structure

The original Transformer follows a classic seq2seq layout:

- **Encoder**: Processes the full input sequence. Each encoder layer has two sub-layers: multi-head self-attention and a position-wise feed-forward network. Both use residual connections + layer normalization.
- **Decoder**: Generates the output sequence autoregressively. Each decoder layer has **three** sub-layers: masked multi-head self-attention, encoder-decoder (cross) attention, and a feed-forward network.

The encoder stacks N identical layers (N=6 in the original paper). The decoder mirrors this with N identical layers. Output from the encoder is fed into every cross-attention layer of the decoder.

## Self-Attention Mechanism

Self-attention allows every token in a sequence to attend to every other token. For each token, three vectors are computed: **Query (Q)**, **Key (K)**, and **Value (V)** via learned linear projections.

The attention score between token i and token j is: `score(i, j) = (Q_i · K_j) / sqrt(d_k)`

Scores are softmaxed to get attention weights, which are then used to compute a weighted sum of Value vectors. This gives each token a representation that is a blend of the entire sequence, weighted by relevance.

## Multi-Head Attention

Instead of a single attention function, the Transformer runs **h parallel attention heads** (h=8 in the original), each with its own Q/K/V projections of dimension `d_k = d_model / h`. Each head learns different attention patterns (syntactic, semantic, positional, etc.). Outputs of all heads are concatenated and linearly projected to produce the final output.

```python
import torch
import torch.nn as nn
import math

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)

    def forward(self, Q, K, V, mask=None):
        batch, seq_len, _ = Q.shape
        Q = self.W_q(Q).view(batch, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        K = self.W_k(K).view(batch, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = self.W_v(V).view(batch, -1, self.num_heads, self.d_k).transpose(1, 2)

        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))
        weights = torch.softmax(scores, dim=-1)
        output = torch.matmul(weights, V)

        output = output.transpose(1, 2).contiguous().view(batch, seq_len, -1)
        return self.W_o(output)
```

## Feed-Forward Network

Each encoder/decoder layer has a position-wise feed-forward network applied independently to every position. It is a simple two-layer MLP with a ReLU (or GELU) activation in between, expanding from `d_model` to `d_ff` (typically 4x `d_model`) and back.

```
FFN(x) = max(0, xW_1 + b_1)W_2 + b_2
```

The expansion factor (usually 4x) gives the model capacity to learn complex transformations in its intermediate representations.

## Layer Normalization and Residual Connections

Every sub-layer (attention, FFN) is wrapped with:

1. **Residual connection**: `output = sublayer(x) + x` — preserves the original signal and stabilizes gradient flow.
2. **Layer normalization**: `LayerNorm(x + sublayer(x))` — normalizes across the feature dimension for each token independently.

The original paper uses **post-norm** (norm after the residual add). More recent models (GPT-2+, many modern LLMs) use **pre-norm** (norm before the sub-layer), which trains more stably at scale.

## Positional Encoding

Since self-attention is permutation-invariant, positional information must be injected. The original paper uses sinusoidal positional encodings (fixed, not learned). Modern models typically use **learned positional embeddings** added directly to token embeddings. Some use rotary positional embeddings (RoPE) or ALiBi for better length generalization.

```python
def sinusoidal_encoding(max_len, d_model):
    pe = torch.zeros(max_len, d_model)
    position = torch.arange(0, max_len).unsqueeze(1).float()
    div_term = torch.exp(torch.arange(0, d_model, 2).float() * -(math.log(10000.0) / d_model))
    pe[:, 0::2] = torch.sin(position * div_term)
    pe[:, 1::2] = torch.cos(position * div_term)
    return pe
```

## Key takeaways

- Transformers replace recurrence with attention, enabling massive parallelism during training
- The encoder-decoder split is task-dependent: encoders for understanding (classification, NER), decoders for generation (text, code), full encoder-decoder for translation/summarization
- Pre-norm is now standard for large models due to training stability
- Each attention head learns distinct patterns — removing heads degrades performance even if others compensate
- Parameter count is dominated by the Q/K/V projections and FFN layers (~2/3 of total in typical LLMs)

## Common bugs

- Forgetting to apply the **causal mask** in decoder self-attention (allows information leakage from future tokens)
- Incorrect reshaping of multi-head tensors: must be `(batch, heads, seq_len, d_k)` before matmul
- Using post-norm when the code was designed for pre-norm (or vice versa) — causes divergence
- Not accounting for padding tokens in attention scores (mask them to -inf before softmax)
- Applying layer norm to the wrong dimension (should normalize over features, not sequence length)
