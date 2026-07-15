---
topic: agentic-ai
difficulty: hard
tags: [llm, inference, serving, quantization, batching, throughput]
last_sent:
review_count: 0
---

# LLM Serving and Inference

## The Inference Problem

### Training vs Inference
- **Training:** Forward + backward pass; compute-bound; uses all GPU cores
- **Inference:** Forward pass only; memory-bandwidth-bound; bottleneck is reading weights

### Token Generation Loop
1. Prefill: Process entire input prompt in parallel (compute-bound)
2. Decode: Generate one token at autoregressively (memory-bound)
3. Each decode step reads ALL model weights from memory

### Latency Metrics
- **Time to First Token (TTFT):** Prefill latency; depends on prompt length
- **Time Per Output Token (TPOT):** Decode speed; ~30-100ms for 70B model
- **Throughput:** Tokens/second across all concurrent requests
- **P50/P95/P99 latency:** Tail latency matters for SLO compliance

---

## KV Cache

### What It Is
- Stores key and value tensors from previous tokens
- Avoids recomputing attention for entire prompt at each step
- Memory grows linearly with sequence length × num_layers × num_heads × head_dim

### KV Cache Memory
- LLaMA 70B, 4K context: ~40GB KV cache per sequence
- LLaMA 70B, 128K context: ~1.28TB per sequence (!!)
- KV cache quantization can reduce 4-8x

### Optimization Techniques
- **PagedAttention (vLLM):** Virtual memory for KV cache; eliminate fragmentation
- **Prefix caching:** Share KV cache for common prompt prefixes
- **StreamingLLM:** Attention sink tokens + sliding window for infinite context
- **GQA (Grouped Query Attention):** Share KV heads across query heads; reduce KV cache size
- **MLA (Multi-Head Latent Attention):** DeepSeek's approach; compress KV via low-rank projection

---

## Quantization

### Why It Matters
- LLaMA 70B in FP16: 140GB memory → needs 2+ A100 80GB GPUs
- LLaMA 70B in INT4: ~35GB → fits on 1 A100 80GB
- Reduces memory → higher batch size → higher throughput
- Reduces compute → lower latency per token

### Number Formats
| Format | Bits | Use Case |
|---|---|---|
| FP32 | 32 | Training (master weights) |
| BF16 | 16 | Training + inference |
| FP16 | 16 | Inference |
| INT8 | 8 | Inference (post-training) |
| INT4 | 4 | Inference (aggressive compression) |

### Post-Training Quantization Methods
- **GPTQ:** Layer-wise; OBS-based; excellent INT4 quality; needs calibration data
- **AWQ:** Protects important weights (activations-aware); fast; best quality/speed tradeoff
- **GGUF:** llama.cpp format; CPU-friendly; supports mixed precision
- **QuIP#:** Incoherence processing + lattice codebooks; state-of-the-art INT2/INT3

### Quantization-Aware Training (QAT)
- Simulate quantization during training
- Better quality than post-training but expensive
- Useful for edge deployment

---

## Speculative Decoding

### Core Insight: Draft and Verify
1. Small draft model generates K candidate tokens quickly
2. Large target model verifies all K tokens in ONE forward pass
3. Accept matching prefix; reject and resample from first mismatch

### Benefits
- Same distribution as target model (mathematically equivalent)
- 2-3x speedup when draft model is good
- No quality loss (guaranteed by rejection sampling)

### Variants
- **Medusa:** Multiple prediction heads on target model; no draft model needed
- **EAGLE:** Autoregressive draft from target model's hidden states
- **Token Tree Verification:** Branching draft trees; parallel verification

### When It Helps
- High target model latency (large models)
- Good draft-target agreement (similar distributions)
- Latency-bound scenario (not throughput-bound)

---

## Serving Frameworks

### vLLM
- PagedAttention for efficient KV cache
- Continuous batching (iteration-level scheduling)
- Tensor parallelism, pipeline parallelism
- Prefix caching, guided generation (structured output)
- OpenAI-compatible API

### TGI (Text Generation Inference)
- Hugging Face's production server
- Flash Attention, KV cache management
- Continuous batching, token streaming
- Quantization support (GPTQ, AWQ, bitsandbytes)

### TensorRT-LLM
- NVIDIA's optimized inference engine
- Custom CUDA kernels for maximum performance
- FP8/INT4 quantization, in-flight batching
- Best raw performance on NVIDIA hardware

### llama.cpp
- CPU inference (GGML/GGUF format)
- Quantized models for edge devices
- Metal (Apple Silicon) and CUDA acceleration
- Ideal for local/edge deployment

---

## Serving Architecture Patterns

### Continuous Batching
- Traditional: wait for all requests to complete before new batch
- Continuous: add/remove requests at each iteration
- Much higher throughput; lower tail latency

### Disaggregated Prefill/Decode
- Separate GPU clusters for prefill (compute-bound) and decode (memory-bound)
- Prefill nodes: high compute utilization
- Decode nodes: optimized for memory bandwidth
- Connected via high-speed network

### Chunked Prefill
- Break long prefill into chunks
- Interleave with decode steps
- Prevents prefill from blocking decode requests

---

## Parallelism for Large Models

### Tensor Parallelism
- Split individual layers across GPUs
- Each GPU holds a portion of each weight matrix
- Requires all-reduce communication at each layer
- Good for: single-node multi-GPU (NVLink)

### Pipeline Parallelism
- Split model into stages; each stage on different GPU
- Micro-batching to keep all GPUs busy
- Bubble overhead (some GPUs idle during pipeline fill/drain)
- Good for: multi-node setups

### Expert Parallelism (MoE)
- Mixture of Experts: only subset of experts activated per token
- Router selects top-K experts per token
- Experts distributed across GPUs
- Reduces active parameters while keeping total capacity high

---

## FlashAttention

### Why It Matters
- Standard attention: O(N^2) memory for N-token sequences
- FlashAttention: IO-aware; tiling avoids materializing full attention matrix
- 2-4x faster than standard attention; enables longer contexts

### How It Works
1. Split Q, K, V into blocks that fit in SRAM
2. Compute attention block-by-block; online softmax trick
3. Never materialize full N×N attention matrix
4. Memory: O(N) instead of O(N^2)

### FlashAttention-2/3
- v2: Better parallelism across sequence length
- v3: FP8 support, async operations on Hopper GPUs

---

## Edge and On-Device Inference

### Challenges
- Limited memory (4-16GB on phones)
- No GPU or limited GPU
- Power constraints
- Thermal limits

### Strategies
- Aggressive quantization (INT4, INT2)
- Model pruning and distillation
- ONNX Runtime, TensorFlow Lite, CoreML
- Hybrid: small model on-device + large model in cloud

---

## Inference-Time Compute Scaling

### The New Scaling Paradigm
- More compute at inference time → better answers
- Chain-of-thought: model "thinks" before answering (more tokens = more reasoning)
- Best-of-N: generate N answers, pick best (verified by reward model or verifier)

### Process Reward Models (PRM)
- Score each reasoning step, not just final answer
- Enable tree search over reasoning paths
- Used in: OpenAI o1, DeepSeek-R1, AlphaProof
