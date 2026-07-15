---
topic: agentic-ai
difficulty: hard
tags: [llm, serving, frameworks, parallelism]
last_sent:
review_count: 0
---

# LLM Serving Frameworks & Parallelism

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

## Serving Architecture Patterns

### Continuous Batching
- Traditional: wait for all requests to complete before new batch
- Continuous: add/remove requests at each iteration
- Much higher throughput; lower tail latency

### Disaggregated Prefill/Decode
- Separate GPU clusters for prefill (compute-bound) and decode (memory-bound)
- Prefill nodes: high compute utilization
- Decode nodes: optimized for memory bandwidth

### Chunked Prefill
- Break long prefill into chunks
- Interleave with decode steps
- Prevents prefill from blocking decode requests

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

## FlashAttention

Standard attention: O(N²) memory for N-token sequences. FlashAttention: IO-aware; tiling avoids materializing full attention matrix. 2-4x faster; enables longer contexts.

1. Split Q, K, V into blocks that fit in SRAM
2. Compute attention block-by-block; online softmax trick
3. Never materialize full N×N attention matrix
4. Memory: O(N) instead of O(N²)

## Edge and On-Device Inference

### Challenges
- Limited memory (4-16GB on phones)
- No GPU or limited GPU
- Power and thermal constraints

### Strategies
- Aggressive quantization (INT4, INT2)
- Model pruning and distillation
- ONNX Runtime, TensorFlow Lite, CoreML
- Hybrid: small model on-device + large model in cloud

## Inference-Time Compute Scaling

- More compute at inference time → better answers
- Chain-of-thought: model "thinks" before answering (more tokens = more reasoning)
- Best-of-N: generate N answers, pick best
- **Process Reward Models (PRM):** Score each reasoning step, not just final answer. Used in OpenAI o1, DeepSeek-R1, AlphaProof
