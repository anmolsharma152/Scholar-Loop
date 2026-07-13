---
topic: papers
difficulty: hard
last_sent:
review_count: 0
tags:
  - paper
  - gemini
  - long-context
  - multimodal
  - mixture-of-experts
  - retrieval
  - in-context-learning
---

# Gemini 1.5: Unlocking Multimodal Understanding Across Millions of Tokens of Context

**Authors:** Gemini Team, Google
**Published:** arXiv preprint, updated December 2024
**arXiv:** 2403.05530v5

## Problem & Motivation

Previous LLMs were limited to context windows of 8K-128K tokens, requiring complex RAG pipelines for long documents. Models could not process entire codebases, books, or multi-hour videos in a single context. In-context learning was restricted to a handful of examples. RAG systems require external indexing infrastructure and can miss relevant information. The goal was to build a model that can process millions of tokens of context with near-perfect recall, enabling new paradigms like learning to translate a language from a single book entirely in-context.

## Key Idea / Architecture

### Mixture-of-Experts (MoE) Architecture

Gemini 1.5 uses a sparse MoE transformer that enables scaling to massive context lengths without proportional compute increases. Two variants: Gemini 1.5 Pro (largest, most capable) and Gemini 1.5 Flash (smaller, faster, minimal quality regression). The February 2024 Pro version was improved with additional pre-training and post-training iterations yielding >10% relative improvement across benchmarks.

### Native Multimodal Support

Models are natively multimodal, processing text, images, video (sampled at 1 FPS), and audio signals at 16kHz from Universal Speech Model features. The context window reaches 1 million tokens with experiments extending to 10 million tokens. Video frames and audio can be interleaved naturally with text as part of the model input.

### Key Innovations

Retrieval-free long-context processing eliminates the need for complex indexing pipelines. Many-shot in-context learning scales to thousands of examples (up to 4K shots). Cross-modal reasoning combines information from text, images, and audio in a single query. The in-context language learning result demonstrates learning to translate Kalamang from a grammar book provided in context.

## Key Contributions

1. Million-token context with near-perfect recall: >99.7% up to 1M tokens across text, video, and audio modalities
2. In-context language learning (MTOB): translates English to Kalamang (endangered language, <200 speakers) from a grammar book, achieving 5.46/6 quality vs 5.60 for human language learner
3. Many-shot ICL scaling to thousands of examples, consistently outperforming GPT-4 Turbo on low-resource translation
4. Long-document QA without retrieval: full-context Gemini 1.5 Pro beats RAG with 4K chunks 78% of the time on Les Miserables (710K tokens)

## Results (Specific Numbers)

### Needle-in-Haystack Recall

- **Text**: >99.7% recall up to 1M tokens, >99.2% at 10M tokens
- **Video**: >99% recall across 10.5 hours of video (37,994 frames at 1 FPS)
- **Audio**: >99% recall across 107 hours of audio
- **Multiple needles**: >60% recall at 1M tokens with 100 unique needles

### Benchmark Improvements (Feb to May 2024)

- **MATH**: 58.5% to 67.7%
- **GPQA**: 41.5% to 46.2%
- **MathVista**: 52.1% to 63.9%
- **InfographicVQA**: 71.9% to 82.6%

### Long-Context Tasks

- **Kalamang translation** (human eval): Kalamang-to-English 4.14/6, English-to-Kalamang 5.46/6 (human learner: 5.52/5.60)
- **1H-VideoQA**: 56.3% accuracy on hour-long video QA
- **EgoSchema**: 45.2% on egocentric video understanding
- **15-min video ASR**: 5.5% WER (vs Whisper 7.3%, USM 8.8%)

### Win-rates vs Previous Models

- **vs Gemini 1.0 Pro**: 44/50 benchmarks won (88.0%)
- **vs Gemini 1.0 Ultra**: 35/45 benchmarks won (77.8%)
- **vs Gemini 1.5 Pro Feb**: 25/32 benchmarks won (78.1%)

### MRCR Benchmark

- Overtakes Claude 3 Opus at ~32K tokens, maintains ~75% score at 1M tokens

## Why It Matters / Impact

Gemini 1.5 represented a generational leap in long-context capability, shifting the paradigm from RAG-dependent architectures to direct full-document processing. The million-token context enabled processing entire codebases, books, and hours of video in a single pass. The in-context language learning result demonstrated a surprising new capability of LLMs. Despite using significantly less compute than Gemini 1.0 Ultra, Gemini 1.5 Pro outperformed it on the majority of benchmarks (35/45).

## Weaknesses / Limitations

- Processing 1M+ tokens remains computationally expensive despite MoE efficiency
- Multiple-needle retrieval shows degradation beyond ~100 needles at 1M tokens
- Model may mix languages in multilingual contexts
- Pro model not fully accessible for independent research
- Existing benchmarks do not adequately test million-token capabilities
- Hallucination risk increases as context grows—verification becomes harder
- Professional productivity gains (26-75% time savings) measured in controlled settings only

## Follow-up Work / Key References

- Gemini 1.5 Flash — further efficiency optimization for deployment
- Gemini 2.0 (2024) — agentic capabilities building on long-context foundation
- Many-shot ICL research — scaling in-context learning to thousands of examples
- Long-context benchmarks development for million-token evaluation
- Kamradt (2023) — original needle-in-a-haystack evaluation idea
