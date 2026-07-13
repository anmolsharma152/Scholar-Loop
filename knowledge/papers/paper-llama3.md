---
topic: papers
difficulty: hard
tags: [paper, llama3, scaling, open-source, multilingual]
---

# The Llama 3 Herd of Models

**Authors:** Llama Team, AI @ Meta
**Published:** 2024
**arXiv:** 2407.21783

## Problem & Motivation

Building high-quality foundation models requires balancing three key levers:
1. **Data quality and diversity** - Better data leads to better models
2. **Scale** - Larger models with more training compute
3. **Managing complexity** - Simple, reliable architectures scale better

Previous Llama models showed promise but needed more scale and better data. The goal: build the best open-source language model at the time.

## Key Idea / Architecture

### Pre-training

**Data:** 15T multilingual tokens (vs 1.8T for Llama 2)
- 50% general knowledge, 25% math/reasoning, 17% code, 8% multilingual
- Rigorous de-duplication and quality filtering
- Custom pipelines for code and math extraction

**Training:**
- 405B parameter flagship model
- 3.8 × 10²⁵ FLOPs (50x more than Llama 2)
- 16K H100 GPUs
- 8K initial context, extended to 128K

### Architecture

Standard dense Transformer with key modifications:
- **Grouped Query Attention (GQA):** 8 key-value heads (improves inference)
- **128K vocabulary:** Better multilingual support (100K tiktoken + 28K custom)
- **RoPE base frequency:** 500,000 (better long-context support)
- **SwiGLU activation function**
- **No architectural changes from Llama 2** - Performance gains from data and scale

### Post-training

**Supervised Fine-Tuning (SFT):**
- High-quality instruction data
- Rejection sampling for best responses

**Direct Preference Optimization (DPO):**
- No RLHF (simpler and more stable)
- Aligns with human preferences

**Multiple rounds:**
- Iterative improvement with new capabilities
- Tool use, code, reasoning integrated

### Model Sizes

| Model | Parameters | Context | Training |
|-------|------------|---------|----------|
| Llama 3.1 8B | 8B | 128K | July 2024 |
| Llama 3.1 70B | 70B | 128K | July 2024 |
| Llama 3.1 405B | 405B | 128K | July 2024 |

## Key Contributions

1. **Largest open model** - 405B parameter model with competitive performance
2. **Multilingual support** - 8 languages natively
3. **Long context** - 128K token context window
4. **Tool use** - Native function calling capabilities
5. **Comprehensive evaluation** - Extensive benchmarking across tasks

## Results

- **MMLU:** 87.3 (405B) - competitive with GPT-4
- **HumanEval:** 89.0 (405B) - excellent code generation
- **GSM8K:** 96.8 (405B) - strong mathematical reasoning
- **MGSM:** 91.6 (405B) - multilingual math
- **IFEval:** 88.6 (405B) - instruction following

### Comparison to Closed Models

| Benchmark | Llama 3 405B | GPT-4 | Claude 3.5 Sonnet |
|-----------|--------------|-------|-------------------|
| MMLU | 87.3 | 86.4 | 88.7 |
| HumanEval | 89.0 | 90.2 | 92.0 |
| GSM8K | 96.8 | 94.2 | 96.4 |

## Why It Matters

Llama 3 established Meta as a leader in open-source AI:

1. **Open-source leadership** - Largest and most capable open model
2. **Competitive performance** - Matches or exceeds closed alternatives
3. **Multilingual foundation** - Enables applications in many languages
4. **Research platform** - Foundation for derivatives and research

## Weaknesses

- **Compute cost** - 3.8 × 10²⁵ FLOPs is prohibitive for most researchers
- **Alignment trade-offs** - DPO may not be as effective as RLHF for safety
- **No vision/multimodal** - Language only in this release
- **Safety concerns** - Large models require careful deployment

## Follow-up Work

- **Llama 3.2:** Added vision capabilities
- **Llama 3.3:** Further scaling and improvements
- **Fine-tuned derivatives:** Community-built variants
- **Multimodal extensions:** Vision and speech capabilities