---
difficulty: hard
last_sent: null
review_count: 0
tags:
- attention
- transformer
topic: ml-ai
---

# Attention Mechanisms

Attention is the mechanism that allows models to dynamically focus on relevant parts of the input when producing each element of the output. It computes a weighted combination of values, where the weights are determined by the compatibility between queries and keys. In Transformers, attention has entirely replaced recurrence.

## Scaled Dot-Product Attention

The fundamental attention operation. Given matrices Q, K, V:

```
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V
```

The scaling factor `1/sqrt(d_k)` prevents dot products from growing too large in high dimensions, which would push softmax into regions with vanishing gradients. Without it, training becomes unstable.

```python
import torch
import math

def scaled_dot_product_attention(Q, K, V, mask=None):
    d_k = Q.size(-1)
    scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(d_k)
    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))
    weights = torch.softmax(scores, dim=-1)
    return torch.matmul(weights, V), weights
```

## QKV Matrices

For each token in the input, three vectors are derived via learned linear projections:

- **Query (Q)**: "What am I looking for?" — represents the current token's information need.
- **Key (K)**: "What do I contain?" — represents each token's signal that others can match against.
- **Value (V)**: "What do I actually give?" — the content that is retrieved when attention weights are high.

These projections are learned during training and allow the model to develop rich notions of what is "relevant" in different contexts. The same token can have very different Q/K/V depending on its position and context.

## Self-Attention

When Q, K, and V all come from the **same sequence**, it is self-attention. Every token attends to every other token in the same sequence. This is what gives Transformers their ability to capture long-range dependencies — any token can directly influence any other, regardless of distance.

Self-attention has three variants based on what attends to what:

| Type | Q source | K,V source | Use case |
|------|----------|------------|----------|
| Self-attention | Sequence A | Sequence A | Encoder layers, decoder self-attn |
| Cross-attention | Sequence B | Sequence A | Decoder attending to encoder |
| Masked self-attention | Sequence B | Sequence B (masked) | Autoregressive decoding |

## Cross-Attention

In encoder-decoder models, cross-attention bridges the two sequences. The **decoder** provides the queries, while the **encoder** provides keys and values. This lets each decoder position attend to the most relevant parts of the encoded input.

```python
class CrossAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        self.mha = MultiHeadAttention(d_model, num_heads)
        self.norm = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(0.1)

    def forward(self, decoder_hidden, encoder_output, mask=None):
        # decoder_hidden = query, encoder_output = key/value
        attn_output, weights = self.mha(
            Q=decoder_hidden, K=encoder_output, V=encoder_output, mask=mask
        )
        return self.norm(decoder_hidden + self.dropout(attn_output))
```

## Multi-Head Attention

Running a single attention function limits the model to one "type" of relationship per layer. Multi-head attention splits the representation into `h` parallel heads, each with its own Q/K/V projections of dimension `d_k = d_model / h`.

Each head can specialize: one head might track syntactic dependencies, another coreference, another positional proximity. The outputs are concatenated and linearly projected back to `d_model`.

```python
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        assert d_model % num_heads == 0
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)

    def split_heads(self, x):
        batch, seq_len, _ = x.shape
        return x.view(batch, seq_len, self.num_heads, self.d_k).transpose(1, 2)

    def forward(self, Q, K, V, mask=None):
        Q = self.split_heads(self.W_q(Q))
        K = self.split_heads(self.W_k(K))
        V = self.split_heads(self.W_v(V))

        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))
        weights = torch.softmax(scores, dim=-1)
        context = torch.matmul(weights, V)

        context = context.transpose(1, 2).contiguous().view(Q.size(0), -1, self.num_heads * self.d_k)
        return self.W_o(context)
```

## Attention Masking

Masking is critical for two reasons:

1. **Padding mask**: Hides padding tokens so they don't contribute to attention weights. Without this, padding positions corrupt the representation.
2. **Causal (look-ahead) mask**: In decoders, prevents position i from attending to positions j > i. This enforces autoregressive generation — the model cannot "cheat" by looking at future tokens during training.

```python
def causal_mask(seq_len):
    """Returns a boolean mask where True means allowed."""
    return torch.tril(torch.ones(seq_len, seq_len)).unsqueeze(0).unsqueeze(0)

# For padding: mask out positions where input_ids == pad_token_id
def padding_mask(input_ids, pad_id):
    return (input_ids != pad_id).unsqueeze(1).unsqueeze(2)
```

## Key takeaways

- Scaled dot-product attention is O(n^2) in sequence length — this is the main bottleneck for long sequences
- The scaling factor `sqrt(d_k)` is not optional; without it, gradients vanish during training
- Cross-attention is identical to self-attention except Q comes from one sequence and K,V from another
- Causal masking uses `torch.tril` (lower triangular) — everything above the diagonal is masked
- Attention weights are interpretable but not always meaningful — high weight does not always mean causal influence

## Common bugs

- Swapping K and V in attention computation (produces a valid but incorrect output that is hard to debug)
- Forgetting the causal mask during training — allows label leakage, inflating validation metrics
- Applying the mask before or after scaling inconsistently (must be before softmax, after scaling)
- Not masking padding tokens — causes NaNs or degraded performance when sequences are padded
- Using `masked_fill` with `True` for masking instead of `False` (inverted logic)
- Ignoring that `nn.MultiheadAttention` in PyTorch expects `(seq_len, batch, dim)` by default — transpose if needed
