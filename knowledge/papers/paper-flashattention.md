---
topic: papers
difficulty: hard
tags: [paper, flashattention, io-aware, tiling, gpu-optimization]
---

# FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness

**Authors:** Dao, Fu, Ermon, Rudra, Ré (Stanford)
**Published:** NeurIPS 2022
**arXiv:** 2205.14135

## Problem & Motivation

Transformers are slow and memory-hungry on long sequences because self-attention has O(N²) time and memory complexity. Approximate attention methods reduce compute but often don't achieve wall-clock speedup:

1. **Quadratic memory** - Attention matrix O(N²) must be materialized in HBM
2. **Memory bandwidth bottleneck** - GPU compute is faster than memory access
3. **Approximate methods don't help** - FLOP reduction doesn't always translate to speedup

The insight: the bottleneck is memory accesses (IO), not computation.

## Key Idea / Architecture

### IO-Aware Algorithm

FlashAttention uses tiling to avoid materializing the large N×N attention matrix in GPU HBM:

**Key techniques:**
1. **Tiling:** Split Q, K, V into blocks, compute attention on each block
2. **Kernel fusion:** Combine all attention operations into one GPU kernel
3. **Recomputation:** Don't store intermediate attention matrix, recompute in backward pass

### Tiling Algorithm

```
For each block of K, V (loaded to SRAM):
  For each block of Q (loaded to SRAM):
    1. Compute attention scores: S = Q_block @ K_block.T
    2. Compute softmax: P = softmax(S)
    3. Compute output: O = P @ V_block
    4. Update running statistics (for softmax correctness)
```

### IO Complexity

**Standard attention:** O(Nd + N²) HBM accesses
**FlashAttention:** O(N²d²M⁻¹) HBM accesses (M = SRAM size)

For typical values (d=64, M=100KB), FlashAttention requires **9x fewer HBM accesses**.

### Memory Usage

- **Standard attention:** O(N²) memory for attention matrix
- **FlashAttention:** O(N) memory (linear in sequence length)

### Backward Pass

Uses recomputation instead of storing intermediate attention matrix:
- Store output O and softmax statistics (m, l)
- Recompute attention in backward pass using stored statistics
- Even with more FLOPs, faster due to reduced HBM accesses

## Key Contributions

1. **IO-aware attention** - First attention algorithm to account for memory hierarchy
2. **Exact attention** - No approximation, numerically identical to standard attention
3. **Linear memory** - O(N) instead of O(N²)
4. **Kernel fusion** - All attention operations in one GPU kernel
5. **Block-sparse extension** - Supports sparse attention patterns

## Results

- **BERT-large:** 15% faster training than MLPerf 1.1 record
- **GPT-2:** 3x speedup over HuggingFace, 1.8x over Megatron
- **Long-range arena:** 2.4x faster than baselines
- **Memory:** Up to 20x more memory efficient than standard attention
- **Long sequences:** First Transformer to solve Path-X (seq length 16K)

### Scaling

- Sequence length 512: FlashAttention 3x faster than standard
- Sequence length 2K: Still faster than most approximate methods
- Sequence length 16K-64K: Enables new capabilities

## Why It Matters

FlashAttention changed how attention is implemented:

1. **Industry standard** - Now used in most Transformer implementations
2. **Enabled long context** - Made 100K+ token context windows practical
3. **Hardware-algorithm co-design** - Showed importance of IO awareness
4. **Foundation for efficiency** - Led to FlashAttention-2, PagedAttention

## Weaknesses

- **Implementation complexity** - Requires custom CUDA kernels
- **Hardware specific** - Optimized for GPU memory hierarchy
- **Not algorithmic improvement** - Same FLOPs as standard attention
- **Limited sparsity support** - Block-sparse is good but not universal

## Follow-up Work

- **FlashAttention-2:** Improved performance and multi-GPU support
- **PagedAttention:** Applied tiling to KV cache management
- **FlashDecoding:** Optimized inference for long sequences
- **Ring Attention:** Distributed attention across multiple GPUs