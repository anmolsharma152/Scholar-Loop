---
topic: papers
difficulty: hard
last_sent:
review_count: 0
tags:
  - paper
  - distributed-training
  - memory-optimization
  - large-scale
  - parallelism
---

# ZeRO: Memory Optimizations Toward Training Trillion Parameter Models

**Authors:** Samyam Rajbhandari, Jeff Rasley, Olatunji Ruwase, Yuxiong He (Microsoft Research)
**Published:** High Performance Computing, Networking, Storage and Analysis (SC'20)
**arXiv:** 1910.02054

## Problem & Motivation

Training large language models requires enormous GPU memory for model parameters, optimizer states, and gradients. For a model with Φ parameters and single-precision (FP32) weights, standard data parallelism requires each GPU to store a complete replica. With Adam optimizer, each parameter needs 12 bytes (4 for weights + 8 for optimizer states), meaning a 1.5B parameter model requires 18GB per GPU—exceeding the 16GB of a V100. For 100B+ parameter models, hundreds of GPUs are required just to fit the model, let alone train it. Existing solutions like model parallelism, gradient checkpointing, and CPU offloading had severe limitations in efficiency or applicability.

## Key Idea / Architecture

ZeRO (Zero Redundancy Optimizer) partitions optimizer states, gradients, and parameters across data parallel processes, eliminating the memory redundancy of maintaining complete copies on every GPU.

**Stage 1 – Optimizer State Partitioning (P_os):** Each GPU stores only 1/N of the optimizer state, where N is the number of data parallel GPUs. For Adam: each GPU holds Φ/4 bytes instead of 2Φ bytes—a 4× reduction. Gradients are all-reduced after the backward pass (standard DDP behavior), and each GPU updates only its assigned Φ/N parameters.

**Stage 2 – Gradient Partitioning (P_os+g):** In addition to Stage 1, each GPU releases gradient memory for parameters it does not own after the all-reduce, keeping only Φ/N gradient values. This provides 8× memory reduction per GPU (from 12Φ down to ~Φ/N + 2Φ bytes), with no additional communication cost—gradients are reduced and immediately discarded for non-owned parameters.

**Stage 3 – Parameter Partitioning (P_os+g+p):** Each GPU stores only 1/N of parameters. During forward/backward, parameters are gathered from other GPUs via all-gather, used locally, then released. This provides 64× memory reduction, allowing training of 600B+ parameters on 512 GPUs. Communication volume doubles vs. DDP (all-reduce replaced by all-gather twice + reduce-scatter once), but this overhead is minimal with high-bandwidth interconnects.

**The 3D Parallelism Framework:** ZeRO is designed to combine with tensor model parallelism and pipeline parallelism. For a 100B parameter model:
- Tensor parallelism (tp=8) handles layer-internal parallelism across 8 GPUs within a node.
- ZeRO Stage 3 (dp=512) distributes across nodes for memory savings.
- Pipeline parallelism (pp=4) handles sequential layers across nodes.

**Offloading optimization:** ZeRO-Offload (Stage 1-3 + CPU) offloads optimizer states and gradient updates to CPU memory, enabling 100B+ parameter training on a single GPU with ~50× memory reduction. ZeRO-Infinity extends this to NVMe SSDs for near-infinite memory.

## Key Contributions

1. Three-stage memory optimization systematically eliminating redundancy in data parallelism, each stage independently useful.
2. Mathematical proof that Stage 3 communication overhead is only 1.5× DDP for large models (15% extra bandwidth with large Δ = Φ/Pbatch).
3. 3D parallelism framework combining ZeRO with tensor and pipeline parallelism for practical training of 100B+ models.
4. ZeRO-Offload achieving single-GPU training of 100B parameter models at 10 TFLOPS via CPU-GPU collaboration.

## Results (Specific Numbers)

- Stage 1: 4× memory reduction per GPU; identical throughput to DDP (142.4 TFLOPS vs. 145.6 TFLOPS on 1024 GPUs)
- Stage 2: 8× memory reduction; near-identical throughput (144.1 TFLOPS vs. 145.6 TFLOPS, 1% overhead)
- Stage 3: 64× memory reduction; throughput 141.4 TFLOPS (2.9% overhead) at 1024 GPUs
- ZeRO-1024: 100B parameter model trained on 1024 GPUs (4.5 TB total memory), 15 PetaFLOPS sustained
- 1.5B parameter model: fits in 16GB GPU with ZeRO Stage 1 alone (vs. 18GB without ZeRO)
- 100B model: 15.3 GB GPU memory with Stage 3 (vs. 1,000+ GB without)
- ZeRO-Offload: 100B parameter model on 1 GPU at 10 TFLOPS (vs. requiring 1000 GPUs without)
- Communication cost Stage 3: 15.2 TB (all-gather) + 7.6 TB (reduce-scatter) vs. 15.2 TB (all-reduce) for DDP
- Memory breakdown per GPU (100B model, 1024 GPUs): parameters 0.196 GB, gradients 0.392 GB, optimizer states 1.563 GB, activations 11.2 GB
- Stage 1-3 communication breakdown: all-reduce (Stage 1-2) vs. all-gather + reduce-scatter (Stage 3), total bandwidth 75% higher at Stage 3

## Why It Matters / Impact

ZeRO became the foundational memory optimization framework for distributed deep learning. Microsoft's DeepSpeed library implements all three stages and is used by major LLM projects including BLOOM, Phi, and Falcon. The 3D parallelism approach—tensor parallelism within nodes, pipeline parallelism across nodes, ZeRO across data-parallel groups—became the standard recipe for training large models. ZeRO-Infinity enabled training of trillion-parameter models on modest hardware clusters.

## Weaknesses / Limitations

1. Stage 3 communication volume is 1.5× DDP for typical batch sizes; at very large batch sizes (Δ ≈ 1), this ratio drops to ~1×, but large batches hurt training efficiency.
2. The all-gather and reduce-scatter operations in Stage 3 create memory fragmentation that can reduce practical capacity by ~10-15%.
3. Pipeline parallelism (required for 3D parallelism) introduces pipeline bubbles; the paper reports 15-20% idle time for typical configurations.
4. ZeRO-Offload shifts computation to CPU, achieving only ~10 TFLOPS vs. 145+ TFLOPS on GPU—useful for accessibility but not for high-performance training.
5. The analysis assumes homogeneous GPU clusters; heterogeneous or multi-node settings may not achieve the theoretical memory savings due to stragglers.

## Follow-up Work

- DeepSpeed (Microsoft): Production implementation of ZeRO with stages 1-3 plus offloading to CPU/NVMe.
- ZeRO++ (2022): Quantized weights communication and hierarchical partitioning for bandwidth-constrained clusters.
- Megatron-DeepSpeed: Integration of ZeRO with Megatron-LM tensor parallelism for training BLOOM-176B.
- FSDP (PyTorch): Fully Sharded Data Parallel implementing Stage 3 in PyTorch core.
- ZeRO-3 Infinity: Extension to NVMe SSDs enabling near-infinite memory for trillion-parameter training.
- ZeRO-1000: Scaled to 1000 GPUs with 100B parameters, achieving 15 PetaFLOPS sustained throughput.
