---
topic: papers
difficulty: hard
tags: [paper, palm, llm]
last_sent:
review_count: 0
---

# PaLM: Scaling to 540 Billion Parameters

**Authors:** Aakanksha Chowdhery, Sharan Narang, Jacob Devlin, et al. (Google)
**Published:** arXiv 2022 (2204.02311)

## Architecture & Training

PaLM is a dense decoder-only Transformer. Key architectural choices:

- **SwishGLU activation:** Swish(x·W)·V, improving over standard GeLU. Swish(x) = x·σ(x). SwishGLU increases FFN parameters by 33% but produces better quality per FLOP.
- **Parallel attention + FFN:** Attention and FFN computed in parallel then combined: y = x + MHSA(LayerNorm(x)) + FFN(LayerNorm(x)). This speeds up training by ~15% with no quality loss.
- **Multi-query attention** (MQA): All heads share key-value projections; only queries are multi-headed. Reduces memory bandwidth in autoregressive decoding by ~5×.
- **RoPE:** Rotary Position Embeddings applied before attention softmax, enabling better length generalization.

**Training infrastructure:** 6144 TPUv4 chips (768 pods of 8 chips each) in Google's TPU v4 Pods. Training sustained 57.8% MFU (Model FLOPS Utilization) — the key efficiency metric: achieved FLOPs / theoretical peak FLOPs.

**Scale:** 540B parameters trained on 780B tokens. 2.56 × 10²⁴ FLOPs total compute. Largest dense transformer at release (March 2022).

## Dataset & Training

- **780B tokens total** across multiple sources
- Social media conversations (~50%), filtered webpages, books, news articles, code (GitHub)
- Tokenization: 256K token SentencePiece vocabulary (larger than GPT-3's 50K)
- Weight decay, dropout, and label smoothing applied for regularization
- Training used AdaFactor optimizer with separate learning rates per parameter dimension
