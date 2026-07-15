---
topic: papers
difficulty: hard
last_sent:
review_count: 0
tags:
  - paper
  - transfer-learning
  - text-to-text
  - transformers
---

# T5: Text-to-Text Framework & C4 Dataset

**Authors:** Colin Raffel, Noam Shazeer, Adam Roberts, et al. (Google)
**Published:** JMLR 2020 (arXiv 1910.10683)

## Problem & Motivation

The landscape of transfer learning for NLP had grown fragmented, with a diversity of pre-training objectives, architectures, and transfer approaches making it difficult to compare methods. The field needed a comprehensive, controlled comparison across dozens of factors to understand what matters most.

## Key Idea

T5 unifies all text-based language problems into a single "text-to-text" format where every task takes text as input and produces text as output. A task-specific text prefix (e.g., "translate English to German:", "mnli premise:... hypothesis:...") specifies which task to perform, allowing the same model, objective, training procedure, and decoding process across all tasks.

The base architecture is an encoder-decoder Transformer with:
- Simplified layer normalization (no additive bias, placed outside the residual path)
- Relative position embeddings as scalars added to attention logits (32 learned embeddings with logarithmic ranges)

## Colossal Clean Crawled Corpus (C4)

A 750 GB dataset of clean English text from Common Crawl (April 2019). Filtering heuristics include:
- Retaining only lines ending in terminal punctuation
- Discarding pages with fewer than 3 sentences
- Removing pages with offensive words, JavaScript references, lorem ipsum, curly brackets
- Three-sentence span deduplication
- langdetect filters non-English pages (probability ≥ 0.99)

## Pre-Training Objective

The baseline uses a denoising objective that randomly samples and drops out 15% of tokens, replacing consecutive dropped spans with unique sentinel tokens. This outperforms standard language modeling, BERT-style masked LM, and other pre-training objectives.

The baseline model has 220M parameters (roughly 2× BERT-base due to encoder+decoder), is pre-trained for 2^19 = 524,288 steps on C4 (~34B tokens), uses AdaFactor optimizer with inverse square root learning rate schedule.

## Key Contributions

1. Unified text-to-text framework casting every NLP task as text-to-text
2. The C4 dataset, a large-scale cleaned dataset from Common Crawl
3. Comprehensive empirical study comparing pre-training objectives, architectures, datasets, and transfer approaches
4. State-of-the-art results on many benchmarks by combining insights from the systematic study with scale
