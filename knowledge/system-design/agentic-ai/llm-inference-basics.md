---
topic: agentic-ai
difficulty: hard
tags: [llm, inference, kv-cache, quantization]
last_sent:
review_count: 0
---

# LLM Inference: KV Cache & Quantization

## The Inference Problem

### Training vs Inference
- **Training:** Forward + backward pass; compute-bound; uses all GPU cores
- **Inference:** Forward pass only; memory-bandwidth-bound; bottleneck is reading weights

### Token Generation Loop
1. **Prefill**: Process entire input prompt in parallel (compute-bound)
2. **Decode**: Generate one token at a time autoregressively (memory-bound)
3. Each decode step reads ALL model weights from memory

### Latency Metrics
- **Time to First Token (TTFT):** Prefill latency; depends on prompt length
- **Time Per Output Token (TPOT):** Decode speed; ~30-100ms for 70B model
- **Throughput:** Tokens/second across all concurrent requests

## KV Cache

Stores key and value tensors from previous tokens to avoid recomputing attention. Memory grows linearly with sequence length × num_layers × num_heads × head_dim.

- LLaMA 70B, 4K context: ~40GB KV cache per sequence
- LLaMA 70B, 128K context: ~1.28TB per sequence (!!)

### Optimization Techniques
- **PagedAttention (vLLM):** Virtual memory for KV cache; eliminate fragmentation
- **Prefix caching:** Share KV cache for common prompt prefixes
- **StreamingLLM:** Attention sink tokens + sliding window for infinite context
- **GQA:** Share KV heads across query heads; reduce KV cache size
- **MLA:** DeepSeek's approach; compress KV via low-rank projection

## Quantization

- LLaMA 70B in FP16: 140GB memory → needs 2+ A100 80GB GPUs
- LLaMA 70B in INT4: ~35GB → fits on 1 A100 80GB

### Number Formats
| Format | Bits | Use Case |
|---|---|---|
| FP32 | 32 | Training (master weights) |
| BF16 | 16 | Training + inference |
| INT8 | 8 | Inference (post-training) |
| INT4 | 4 | Inference (aggressive compression) |

### Post-Training Quantization Methods
- **GPTQ:** Layer-wise; OBS-based; excellent INT4 quality; needs calibration data
- **AWQ:** Protects important weights (activations-aware); best quality/speed tradeoff
- **GGUF:** llama.cpp format; CPU-friendly; supports mixed precision
- **QuIP#:** Incoherence processing + lattice codebooks; state-of-the-art INT2/INT3

## Speculative Decoding

1. Small draft model generates K candidate tokens quickly
2. Large target model verifies all K tokens in ONE forward pass
3. Accept matching prefix; reject and resample from first mismatch

- Same distribution as target model (mathematically equivalent)
- 2-3x speedup when draft model is good
- No quality loss (guaranteed by rejection sampling)

### Variants
- **Medusa:** Multiple prediction heads on target model; no draft model needed
- **EAGLE:** Autoregressive draft from target model's hidden states
- **Token Tree Verification:** Branching draft trees; parallel verification
