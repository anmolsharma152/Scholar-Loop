---
difficulty: hard
tags:
- paper
- distributed-training
- memory-optimization
- large-scale
- parallelism
topic: papers
last_sent:
review_count: 0
---

# ZeRO: Memory Optimizations Toward Training Trillion Parameter Models

**Authors:** Samyam Rajbhandari, Jeff Rasley, Olatunji Ruwase, Yuxiong He (Microsoft Research)
**Published:** SC'20 (arXiv 1910.02054)

## Problem

Training large models requires enormous GPU memory. For a model with Φ parameters and Adam optimizer, each parameter needs 12 bytes (4 weights + 8 optimizer states). A 1.5B model needs 18GB per GPU — exceeding V100's 16GB. For 100B+ models, hundreds of GPUs are needed just to fit the model. Existing solutions (model parallelism, gradient checkpointing, CPU offloading) had severe limitations in efficiency or applicability.

## Key Idea

ZeRO partitions optimizer states, gradients, and parameters across data parallel processes, eliminating the memory redundancy of maintaining complete copies on every GPU.

**Stage 1 – Optimizer State Partitioning (P_os):** Each GPU stores only 1/N of the optimizer state. For Adam: each GPU holds Φ/4 bytes instead of 2Φ bytes — 4× reduction. Gradients are all-reduced after backward pass, and each GPU updates only its assigned parameters.

**Stage 2 – Gradient Partitioning (P_os+g):** Each GPU releases gradient memory for non-owned parameters after all-reduce, keeping only Φ/N gradient values. 8× memory reduction (from 12Φ down to ~Φ/N + 2Φ bytes) with no additional communication cost.

**Stage 3 – Parameter Partitioning (P_os+g+p):** Each GPU stores only 1/N of all model parameters. When a parameter is needed, it is broadcast from the owning GPU during forward/backward. Reduces memory from ~Φ (parameters) down to Φ/N. N=64 with 1.5B params: 24MB vs 6GB.

## Results

- ZeRO-100B: Trained a 100B parameter model at 15 PetaFLOPs throughput (38.6 TFLOPS per V100, 49.2% MFU)
- ZeRO-1.5B on 64 GPUs: Stage 3 uses 6.9GB vs. deepspeed baseline 24.1GB (3.5× reduction)
- SuperGlue: RoBERTa-large with ZeRO-100B achieves 89.0 vs. baseline 88.5
- Scalability: nearly linear speedup from 64 to 4000 GPUs
- Communication overhead: Stage 1+2 ≈ 0% overhead vs DDP; Stage 3 ≈ 50% increase in communicated data

## Impact

ZeRO made large model training accessible without custom hardware or complex model parallelism. DeepSpeed's ZeRO is the standard approach for training models up to hundreds of billions of parameters on commodity GPU clusters.
