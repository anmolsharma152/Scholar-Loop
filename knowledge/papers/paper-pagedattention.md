---
difficulty: hard
last_sent: 2026-07-13 23:34:32.316879+00:00
review_count: 1
tags:
- paper
- pagedattention
- memory-management
- llm-serving
- virtual-memory
topic: papers
---

# Efficient Memory Management for Large Language Model Serving with PagedAttention

**Authors:** Kwon et al. (UC Berkeley)
**Published:** SOSP 2023
**arXiv:** 2309.06180

## Problem & Motivation

Serving LLMs efficiently requires batching multiple requests, but the KV cache memory is problematic:

1. **Dynamic growth** - KV cache grows/shrinks as tokens are generated
2. **Fragmentation** - Pre-allocating maximum length wastes memory
3. **No sharing** - Can't share KV cache across requests or within beam search
4. **Memory waste** - Existing systems waste up to 80% of KV cache memory

The insight: borrow virtual memory and paging from operating systems.

## Key Idea / Architecture

### PagedAttention

Divide KV cache into fixed-size blocks (like virtual memory pages):

- **Logical blocks** - Contiguous in request's view
- **Physical blocks** - Can be non-contiguous in GPU memory
- **Block table** - Maps logical to physical blocks

### How It Works

1. **KV cache partitioned** into blocks of B tokens each
2. **Blocks allocated on demand** - No pre-allocation
3. **Non-contiguous storage** - Blocks can be scattered in memory
4. **Copy-on-write** - Share blocks until modification needed

### Memory Management

**Block allocation:**
- No pre-allocation for maximum length
- Allocate blocks as tokens are generated
- Free blocks when request completes

**Memory waste:**
- Only internal fragmentation within last block (up to B-1 tokens)
- No external fragmentation (all blocks same size)
- No reserved memory for future tokens

### Sharing Mechanisms

**Parallel sampling:** Share prompt blocks across multiple outputs
- Multiple outputs from same prompt share initial blocks
- Copy-on-write when outputs diverge

**Beam search:** Share blocks across beam candidates
- Common prefix blocks shared
- Reference counting for safe sharing

**Prefix sharing:** Share common prefixes across requests
- System prompts can be shared across requests
- Reduces memory for repeated prompts

### vLLM Architecture

Built on PagedAttention:
- Centralized scheduler for coordination
- Distributed GPU workers
- KV cache manager with block-level management
- Supports GPT, OPT, Llama, etc.

## Key Contributions

1. **PagedAttention algorithm** - Attention with non-contiguous KV cache
2. **Near-zero memory waste** - Only last block has waste
3. **Efficient sharing** - Copy-on-write for parallel decoding
4. **vLLM serving system** - Production-ready implementation

## Results

- **Throughput:** 2-4x improvement over FasterTransformer and Orca
- **Memory efficiency:** Near-zero waste (vs 60-80% in existing systems)
- **Long sequences:** Better performance with longer sequences
- **Beam search:** Significant memory savings with sharing
- **Parallel sampling:** Efficient multi-output generation

### Comparison

| System | KV Cache Waste | Throughput |
|--------|----------------|------------|
| FasterTransformer | ~60% | 1x |
| Orca | ~40% | 1.5x |
| vLLM | <5% | 3.5x |

## Why It Matters

PagedAttention revolutionized LLM serving:

1. **Industry standard** - vLLM is widely used for LLM serving
2. **Democratized serving** - Made LLM serving more accessible
3. **Enabled longer sequences** - Memory efficiency allows longer context
4. **Foundation for optimizations** - Prefix caching, speculative decoding

## Weaknesses

- **Block size trade-off** - Larger blocks = more waste, smaller blocks = more overhead
- **No preemption across requests** - Limited by GPU memory
- **Complexity** - More complex than simple contiguous allocation
- **Limited sharing patterns** - Only works for certain decoding algorithms

## Follow-up Work

- **Continuous batching:** Dynamic request scheduling
- **Prefix caching:** Reuse KV cache for common prefixes
- **Speculative decoding:** Generate multiple tokens in parallel
- **Disaggregated serving:** Separate prefill and decode phases