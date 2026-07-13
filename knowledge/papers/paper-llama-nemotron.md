---
topic: papers
difficulty: hard
last_sent:
review_count: 0
tags:
  - paper
  - reasoning
  - open-source
  - nvidia
  - efficient-inference
---

# Llama-Nemotron: Efficient Reasoning Models

**Authors:** NVIDIA (NVIDIA Research)
**Published:** arXiv September 2025
**arXiv:** 2505.00949

## Problem & Motivation

Reasoning models like OpenAI o1 and DeepSeek-R1 achieve state-of-the-art performance through long chains of thought, self-verification, and reflection, but their long responses create massive inference costs. Inference efficiency is no longer just a deployment concern—it is a core limiting factor for agentic pipelines and the viability of reasoning at scale. Users also need the ability to toggle reasoning on or off for different queries, since not all problems benefit from detailed multi-step reasoning. The authors wanted to build open-source reasoning models that are both highly capable and inference-efficient, competing with DeepSeek-R1 (671B) while fitting on a single 8xH100 node. DeepSeek-R1 requires 8xH200 due to its 671B size, creating practical deployment challenges.

## Key Idea / Architecture

The Llama-Nemotron family consists of three models: Nano (8B), Super (49B), and Ultra (253B). The models are constructed through a five-stage pipeline. First, inference efficiency is optimized using the Puzzle neural architecture search (NAS) framework, which transforms large LLMs into hardware-efficient variants by building a library of alternative transformer blocks (attention removal, variable FFN dimensions, GQA with different KV-head counts) and selecting optimal configurations via mixed-integer programming. LN-Ultra also applies FFN Fusion, replacing consecutive FFN blocks with fewer, wider layers for improved parallelism.

Second, recovery training uses knowledge distillation (40B tokens for Super, 65B for Ultra) followed by continued pretraining (88B tokens for Ultra). Third, supervised fine-tuning combines standard instruction data with reasoning traces from DeepSeek-R1 across math, code, science, and general domains. Fourth, large-scale reinforcement learning on complex math and STEM datasets enables the student model to surpass its teachers—LN-Ultra achieves a substantial GPQA-D boost during this phase. Fifth, a short alignment phase focuses on instruction following and human preference.

A unique feature is the dynamic reasoning toggle ("detailed thinking on/off") allowing users to switch between standard chat and reasoning modes at inference time without separate models.

```
NAS optimization: Block variants → MIP solver → optimal architecture under constraints
Parallel formulation: y = x + MLP(LayerNorm(x)) + Attention(LayerNorm(x))
```

## Key Contributions

1. First open-source models with a dynamic reasoning toggle, enabling users to switch between standard chat and reasoning modes during inference
2. LN-Ultra outperforms DeepSeek-R1 (671B) while fitting on a single 8xH100 node, achieving 5x throughput over Llama 3.3-70B-Instruct
3. Demonstrated that aggressive NAS-based architecture optimization can be reconciled with high performance through distillation and continued pretraining
4. Released the complete post-training dataset, training codebases (NeMo, NeMo-Aligner, Megatron-LM), and all model checkpoints
5. Developed custom large-scale RL training framework with FP8 generation optimizations
6. Curated large-scale synthetic reasoning datasets: 488K Python code samples from 28,904 competitive programming questions, math problems from AoPS forums filtered and augmented

## Results (Specific Numbers)

- GPQA Diamond: LN-Ultra 97.3% (vs. DeepSeek-R1 71.5%, Llama 3.1 405B 43.4%)
- AIME 2024: LN-Ultra 97.0% (vs. DeepSeek-R1 79.8%)
- AIME 2025: LN-Ultra 89.5% (vs. Llama 4 Maverick 69.8%)
- MATH 500: LN-Ultra 97.3%
- LiveCodeBench (24.10-25.02): LN-Ultra 74.1%
- IFEval: LN-Ultra 88.8%
- MMLU: 88.1% (vs. Llama 3.1 405B 88.6%)
- HumanEval: 88.4% (vs. Llama 3.1 405B 86.0%)
- Throughput: 5x speedup over Llama 3.3-70B-Instruct at batch size 256, TP1
- LN-Ultra fits on a single 8xH100 node (supports up to 3M cached tokens at FP8)

## Why It Matters / Impact

Llama-Nemotron democratizes reasoning capabilities by providing the most capable open-source reasoning models with commercially permissive licensing. LN-Ultra being the "most intelligent open model" (per Artificial Analysis) while fitting on a single node is significant for enterprise deployment. The dynamic reasoning toggle is a practical innovation—users can allocate compute judiciously, using reasoning only when needed. The full release of post-training data and codebases enables the research community to build on these methods. The five-stage training pipeline provides a practical blueprint for building efficient reasoning models from existing base models, demonstrating that NAS-optimized architectures can match or surpass their original teachers.

## Weaknesses / Limitations

- 253B parameters still require significant hardware (8xH100 node) for optimal serving, limiting accessibility for smaller organizations
- Knowledge distillation from proprietary teachers (DeepSeek-R1) introduces dependency on those models and their licensing terms
- The continued pretraining phase (88B tokens) adds substantial compute cost beyond the original Llama 3 base model
- Limited evaluation on non-English languages and multimodal tasks in this report
- The Puzzle NAS framework adds complexity to the training pipeline and may not generalize to all architectures
- The reasoning toggle is binary (on/off) rather than supporting granular control over reasoning depth or token budget
- Code data contamination check showed <0.3% overlap with benchmarks, but this validation may not generalize to all domains
- The knowledge distillation training uses 488K Python code samples, which may limit generalization to other programming languages

## Follow-up Work

- Llama-Nemotron-Ultra-253B-CPT: extended continued pretraining variant for specific domains
- Integration into NVIDIA's enterprise AI platform (NVIDIA AI Enterprise)
- Scaling the NAS approach to even larger models and diverse hardware targets
- Open-source RL environments enabling community-driven reasoning improvements

---
