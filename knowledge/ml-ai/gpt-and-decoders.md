---
difficulty: medium
last_sent: null
review_count: 0
tags:
- gpt
- decoder
- llm
topic: ml-ai
---

# GPT and Decoder Models

GPT (Generative Pre-trained Transformer, Radford et al. 2018) introduced the decoder-only Transformer to NLP. Instead of encoding a full input bidirectionally, GPT generates text **one token at a time**, left to right, using only previous tokens as context. This autoregressive design made GPT the foundation for modern large language models (GPT-4, Claude, LLaMA, etc.).

## Decoder-Only Architecture

GPT uses the **decoder** portion of the Transformer without cross-attention. There is no encoder — the model only sees previously generated tokens. Each layer has:

1. **Masked multi-head self-attention** — each token attends to itself and all previous tokens, but never future tokens
2. **Feed-forward network** — position-wise MLP
3. Residual connections + layer normalization around both sub-layers

This simpler architecture (compared to encoder-decoder) scales extremely well and is the basis for all modern LLMs.

```python
import torch
import torch.nn as nn

class GPTBlock(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()
        self.ln1 = nn.LayerNorm(d_model)
        self.attn = nn.MultiheadAttention(d_model, num_heads, batch_first=True)
        self.ln2 = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Linear(d_ff, d_model),
            nn.Dropout(dropout),
        )

    def forward(self, x, mask):
        # Pre-norm residual: LayerNorm → Attention → Residual
        normed = self.ln1(x)
        attn_out, _ = self.attn(normed, normed, normed, attn_mask=mask)
        x = x + attn_out

        # Pre-norm residual: LayerNorm → FFN → Residual
        x = x + self.ffn(self.ln2(x))
        return x
```

## Autoregressive Generation

GPT generates text by predicting the next token given all previous tokens:

```
P(x_t | x_1, x_2, ..., x_{t-1})
```

At inference, this happens **iteratively**: generate one token, append it to the sequence, generate the next, and repeat until an end-of-sequence token is produced. This is inherently sequential — a key bottleneck compared to encoder models that process all tokens in parallel.

```python
@torch.no_grad()
def generate(model, input_ids, max_new_tokens, temperature=1.0, top_k=None):
    for _ in range(max_new_tokens):
        # Crop to context window if needed
        idx_cond = input_ids[:, -model.context_size:]
        logits = model(idx_cond)[:, -1, :] / temperature

        if top_k is not None:
            v, _ = torch.topk(logits, top_k)
            logits[logits < v[:, [-1]]] = float('-inf')

        probs = torch.softmax(logits, dim=-1)
        next_token = torch.multinomial(probs, num_samples=1)
        input_ids = torch.cat([input_ids, next_token], dim=1)
    return input_ids
```

## Causal Masking

The defining feature of decoder attention. A **causal mask** (lower-triangular) ensures token at position i can only attend to positions ≤ i. During training, all positions are processed in parallel (teacher forcing), but the mask prevents "cheating" — each position only sees its own and previous positions.

```python
def create_causal_mask(seq_len, device):
    mask = torch.triu(torch.ones(seq_len, seq_len, device=device), diagonal=1)
    mask = mask.masked_fill(mask == 1, float('-inf'))
    return mask

# Example: seq_len=4
#  0   -inf -inf -inf
#  0    0   -inf -inf
#  0    0    0   -inf
#  0    0    0    0
```

## Unidirectional vs. Bidirectional

| Property | GPT (Unidirectional) | BERT (Bidirectional) |
|----------|---------------------|---------------------|
| Context | Left-to-right only | Full context |
| Generation | Yes | No |
| Pre-training task | Next token prediction | Masked language modeling |
| Strength | Text generation, code | Understanding, classification |
| Attention mask | Causal (lower-triangular) | None (full attention) |

GPT's unidirectional constraint is both a limitation (less context for understanding) and a strength (naturally suited for generation).

## In-Context Learning

One of the most surprising emergent abilities of large GPT models. Instead of updating weights, the model learns from examples provided in the **prompt** at inference time:

```
Classify the sentiment:
Positive: "I love this movie!" → Positive
Negative: "This was terrible." → Negative
"The cinematography was stunning" → 
```

The model infers the task from context and applies it to the new input — no gradient updates needed. This enables few-shot and zero-shot capabilities that scale with model size.

## Prompt Engineering Basics

Crafting effective prompts is a practical skill for working with GPT-style models:

- **Be specific**: "Summarize in 3 bullet points" beats "Summarize"
- **Provide examples**: Few-shot examples dramatically improve consistency
- **Use system prompts**: Set the role and behavior at the start
- **Chain of thought**: Ask the model to "think step by step" for complex reasoning
- **Temperature**: Lower (0.1-0.3) for factual, higher (0.7-1.0) for creative

```python
# Few-shot prompt template
prompt = """Classify the review sentiment.

Review: "Great product, works perfectly" → Positive
Review: "Broke after one day" → Negative
Review: "It's okay, nothing special" → Neutral

Review: "{input}" → """
```

## Key takeaways

- Decoder-only is the dominant architecture for LLMs — simpler than encoder-decoder, scales better
- Causal masking is what makes autoregressive training parallelizable: mask everything above the diagonal
- In-context learning is an emergent ability that requires sufficient scale (roughly 10B+ parameters)
- Temperature and top-k/top-p sampling control the generation diversity vs. quality tradeoff
- Modern LLMs use pre-norm (LayerNorm before attention/FFN) for stable training at scale

## Common bugs

- Forgetting the causal mask during training — model learns to copy future tokens, metrics look artificially good
- Setting temperature to 0 incorrectly (should take argmax, not softmax of logits at temp=0 — causes NaN)
- Truncating prompts too aggressively — removing few-shot examples or system instructions breaks performance
- Not accounting for tokenization boundaries — splitting mid-word changes meaning in few-shot examples
- Using `model.eval()` inconsistently during generation (dropout/batchnorm behave differently)
- Generating past the model's context window — causes silent errors or garbage output
