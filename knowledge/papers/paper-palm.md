---
difficulty: hard
last_sent: 2026-07-14 11:52:30.720654+00:00
review_count: 1
tags:
- paper
- language-models
- scaling
- pathways
topic: papers
---

# PaLM: Scaling Language Modeling with Pathways

**Authors:** Aakanksha Chowdhery, Sharan Narang, Jacob Devlin, Maarten Bosma, Hyung Won Chung, Noam Shazeer, Jeff Dean et al. (Google Research)
**Published:** JMLR 2022
**arXiv:** 2204.02311

## Problem & Motivation

Prior large language models (GPT-3, GLaM, Gopher, Chinchilla) demonstrated remarkable few-shot learning, but scaling to extremely large model sizes across multiple TPU pods remained an open engineering challenge. Training a 540B-parameter model required new ML infrastructure capable of efficient distributed training across thousands of accelerator chips. The authors wanted to understand whether scaling beyond previous limits would continue to yield improvements or hit diminishing returns, and whether emergent capabilities appear at sufficient scale. Additionally, previous large models were trained on single TPU systems or used pipeline parallelism, limiting achievable scale and efficiency. The GPT-3 scaling laws suggested continued improvement was possible, but had not been tested at 540B parameter scale.

## Key Idea / Architecture

PaLM is a 540-billion parameter, densely activated, autoregressive Transformer language model trained on 780 billion tokens of high-quality text. The architecture builds on the standard decoder-only Transformer with several key modifications. SwiGLU activations replace standard ReLU/GeLU in the MLP layers, using the formulation `Swish(xW) * xV` which requires three matrix multiplications instead of two but yields significant quality improvements in compute-equivalent experiments. Parallel layers replace the standard serialized formulation: instead of `y = x + MLP(LayerNorm(x + Attention(LayerNorm(x))))`, PaLM uses `y = x + MLP(LayerNorm(x)) + Attention(LayerNorm(x))`, enabling ~15% faster training at large scales through fused matrix multiplications. Multi-Query Attention shares key and value projections across heads while keeping query projections per-head, maintaining quality while reducing inference cost. RoPE embeddings replace absolute or relative position embeddings for better long-sequence performance. The model uses no biases in any dense kernels or layer norms, improving training stability. The vocabulary is 256k SentencePiece tokens generated from training data, fully lossless and reversible.

```
SwiGLU: output = Swish(xW) * xV
Parallel block: y = x + MLP(LayerNorm(x)) + Attention(LayerNorm(x))
```

The model comes in three sizes: 8B (32 layers, 16 heads, d_model=4096), 62B (64 layers, 32 heads, d_model=8192), and 540B (118 layers, 48 heads, d_model=18432). Training was performed on 6144 TPU v4 chips across two TPU Pods using the Pathways system, achieving 46.2% model FLOPs utilization and 57.8% hardware FLOPs utilization—efficiency levels not previously achieved at this scale.

## Key Contributions

1. Demonstrated the first large-scale use of the Pathways ML system, training a single model across 6144 TPU v4 chips with pipeline-free training and high hardware utilization
2. Achieved state-of-the-art few-shot results on hundreds of language understanding and generation benchmarks, with new SOTA on 28 of 29 widely-evaluated English NLP tasks
3. Showed breakthrough capabilities on BIG-bench, outperforming average human performance on this recently released benchmark of 150+ difficult tasks
4. Discovered discontinuous improvements—roughly 25% of BIG-bench tasks showed dramatic jumps when scaling from 62B to 540B, suggesting emergent capabilities at scale
5. Demonstrated that few-shot chain-of-thought prompting at 540B scale can match or outperform finetuned state-of-the-art on multi-step reasoning tasks
6. Provided comprehensive bias and toxicity analysis, finding that model-generated continuations correlate with prompt toxicity more than human-generated continuations do

## Results (Specific Numbers)

- MMLU (5-shot): 69.3% (PaLM 540B) vs. 43.9% (GPT-3 175B), new SOTA
- BIG-bench (mixed): outperforms average human performance on 65% of tasks
- The 62B model sits between 8B and 540B, following smooth scaling laws for most benchmarks
- TriviaQA (1-shot): 86.1% (PaLM 540B)
- Math benchmarks: 58.8% on MATH (with chain-of-thought prompting)
- Discontinuous improvements on ~25% of BIG-bench tasks from 62B→540B scale
- Training efficiency: 46.2% model FLOPs utilization, 57.8% hardware FLOPs utilization on 6144 TPU v4 chips
- Code generation: state-of-the-art on HumanEval and MBPP benchmarks
- Translation: new SOTA across multiple language pairs (English-German, English-French, etc.)
- Memorization: analysis shows memorization increases with model scale, but remains limited for longer sequences
- Winogender coreference: new SOTA in 1-shot and few-shot settings with PaLM 540B

## Why It Matters / Impact

PaLM established that scaling improvements in language models had not plateaued, demonstrating both continuous and discontinuous improvement patterns. The Pathways system proved that training single models across thousands of accelerator chips was feasible with high efficiency, paving the way for Gemini and subsequent Google models. The discovery of emergent capabilities at the 540B scale—where ~25% of BIG-bench tasks showed sudden capability jumps—influenced the direction of scaling research and discussions about compute-optimal training. The model also demonstrated that few-shot prompting with chain-of-thought reasoning could match or exceed finetuned models on multi-step reasoning tasks, shifting the paradigm toward larger, more general models rather than many small task-specific ones. This influenced the development of instruction-following models and the move away from task-specific fine-tuning.

## Weaknesses / Limitations

- Massive compute requirements: 6144 TPU v4 chips make reproduction infeasible for most researchers and even many well-funded labs
- Memorization and bias concerns: the model can reproduce training data verbatim and exhibits stereotypical associations (e.g., associating Muslims with terrorism and violence)
- No instruction finetuning was performed, limiting direct consumer applications and chatbot use cases
- Densely activated 540B parameters make inference expensive compared to sparse alternatives like mixture-of-experts models
- Training instability required careful hyperparameter tuning; loss spikes occurred requiring restart from earlier checkpoints
- The 22% non-English proportion in training data may limit multilingual performance despite strong reported results
- Toxicity of generated continuations correlates with prompt toxicity, more so than with human-generated continuations

## Follow-up Work

- Gopher/Chinchilla: explored compute-optimal training with different scaling strategies, showing PaLM was overtrained
- PaLM 2: Google's follow-up with improved multilingual capabilities, smaller model variants, and more efficient training
- Megatron-Turing NLG: NVIDIA's 530B model using pipeline parallelism across GPU clusters
- Gemini: Google's multimodal model family building on Pathways infrastructure with both text and vision
- Scaling Laws research: further investigation into discontinuous improvements and emergent capabilities at scale
- U-PaLM and UL2: explored mixture-of-denoisers objectives for more versatile language models

---