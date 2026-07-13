---
topic: papers
difficulty: hard
tags: [paper, gpt, few-shot, in-context-learning, large-language-models]
---

# Language Models are Few-Shot Learners

**Authors:** Brown et al. (OpenAI)
**Published:** NeurIPS 2020
**arXiv:** 2005.14165

## Problem & Motivation

Previous work on language models showed they could perform tasks via fine-tuning, but this required:
1. Labeled data for each task
2. Gradient updates to model parameters
3. Separate model checkpoints for each task

The question: can language models perform tasks with just a few examples in the prompt, without any gradient updates? This "in-context learning" capability could make language models more flexible and general-purpose.

## Key Idea / Architecture

GPT-3 is a 175B parameter autoregressive language model (same architecture as GPT-2, just much larger). The key insight is **in-context learning**: the model can learn from examples provided in the prompt without any parameter updates.

### Three Settings

1. **Zero-shot:** Only the task description, no examples
   - Task: "Translate English to French: cheese =>"
   
2. **One-shot:** Task description + one example
   - Task: "Translate English to French: cheese => fromage, sea otter =>"
   
3. **Few-shot:** Task description + a few examples (typically 10-100)
   - More examples in context → better performance

### Scale

- 175 billion parameters
- 96 layers, 12288 hidden size, 96 attention heads
- Training on 300 billion tokens (Common Crawl, filtered)
- 3.14 x 10^23 FLOPs for training
- Trained on V100 GPUs for approximately 34 days

### Key Insight: In-Context Learning

The model learns from the prompt without any gradient updates:
```python
# Few-shot example
prompt = """
Translate English to French:
sea otter => loutre de mer
peppermint => menthe poivrée
plush girafe => girafe en peluche
cheese =>
"""
# Model generates: "fromage"
```

This is fundamentally different from fine-tuning - the model's parameters are frozen.

## Key Contributions

1. **Demonstrated in-context learning at scale** - First convincing evidence that large language models can learn tasks from examples in the prompt
2. **Showed performance improves with scale** - Larger models and more examples in context both help
3. **Achieved competitive results without fine-tuning** - On many benchmarks, few-shot GPT-3 matches or exceeds fine-tuned models
4. **Analyzed task types** - Identified which tasks benefit most from few-shot learning

## Results

- **SuperGLUE:** 71.8 (vs 89.0 for fine-tuned SOTA, but impressive without any training)
- **TriviaQA:** 71.2% (zero-shot) - competitive with supervised approaches
- **LAMBADA:** 76.2% (zero-shot) - 18% improvement over previous SOTA
- **ARC:** 51.4% (zero-shot) - competitive with fine-tuned models
- **Translation:** 11.5 BLEU (English→French, zero-shot) - reasonable without any training

### Key Observations

1. **Performance scales smoothly with model size** - Larger models consistently better
2. **More examples in context help** - Performance improves with more few-shot examples
3. **Task-specific patterns emerge** - Some tasks benefit more from scale than others
4. **Limitations exist** - Performance still lags behind fine-tuned models on many benchmarks

## Why It Matters

GPT-3 fundamentally changed how we think about language models:

1. **Paradigm shift:** From "pre-train then fine-tune" to "pre-train then prompt"
2. **Emergent capabilities:** Scale unlocks qualitatively new abilities (in-context learning)
3. **Reduced task-specific engineering:** No need for labeled data or fine-tuning for many applications
4. **Foundation for future models:** GPT-3.5, GPT-4 built on these insights

## Weaknesses

- **No fine-tuning comparison** - Paper doesn't compare to fine-tuned GPT-3 on all tasks
- **Prompt sensitivity** - Performance can vary significantly with prompt format
- **Inconsistent few-shot performance** - Sometimes more examples don't help
- **Compute cost** - 175B parameters is extremely expensive to train and serve
- **Hallucination and factual errors** - Model can generate plausible but incorrect information

## Follow-up Work

- **InstructGPT:** Fine-tuning with human feedback to align the model
- **Chain-of-thought prompting:** Improved reasoning by showing intermediate steps
- **Tool-use and code generation:** Extending language models beyond text
- **Scaling laws research:** Better understanding of how scale affects performance