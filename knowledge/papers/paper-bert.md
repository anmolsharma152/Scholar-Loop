---
topic: papers
difficulty: hard
tags: [paper, bert, pre-training, nlp, transfer-learning]
---

# BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding

**Authors:** Devlin, Chang, Lee, Toutanova (Google AI Language)
**Published:** NAACL 2019
**arXiv:** 1810.04805

## Problem & Motivation

Previous language model pre-training approaches (like GPT) were unidirectional - they could only condition on left context or right context, but not both. This limited their effectiveness for many downstream tasks:

1. **Sentence-level tasks** (sentiment analysis, QA) benefit from bidirectional context
2. **Token-level tasks** (NER, question answering) need context from both sides
3. Fine-tuning from pre-trained models was already showing promise, but unidirectional constraints hurt performance

The question: how can we pre-train a deep bidirectional model that leverages context from both directions?

## Key Idea / Architecture

BERT (Bidirectional Encoder Representations from Transformers) introduces two key innovations:

### 1. Masked Language Modeling (MLM)

Instead of predicting the next token, BERT randomly masks 15% of input tokens and trains the model to predict the masked tokens. This allows true bidirectional context.

**Masking procedure:**
- 80% of selected tokens are replaced with [MASK]
- 10% are replaced with a random token
- 10% are left unchanged
- The model must predict the original token at all masked positions

### 2. Next Sentence Prediction (NSP)

A binary classification task where the model predicts whether sentence B follows sentence A in the original text. This helps with tasks requiring sentence-pair understanding (QA, natural language inference).

### Architecture

- **BERT-Base:** 12 layers, 768 hidden, 110M parameters
- **BERT-Large:** 24 layers, 1024 hidden, 340M parameters
- Uses the Transformer encoder architecture (not decoder)
- Position embeddings, segment embeddings, token embeddings

**Pre-training data:** BooksCorpus (800M words) + English Wikipedia (2,500M words)

## Key Contributions

1. **First deeply bidirectional pre-trained language model** - Previous work was limited to left-to-right or right-to-left
2. **Simple but powerful pre-training paradigm** - MLM and NSP are intuitive and effective
3. **Effective transfer learning** - Fine-tuning BERT achieves SOTA on 11 NLP tasks with minimal task-specific architecture changes
4. **Open-sourced pre-trained models** - Enabled widespread adoption and research

## Results

- **GLUE benchmark:** 80.5% (7.7% absolute improvement)
- **SQuAD v1.1:** 93.2 F1 / 88.5 EM (2.0+ F1 improvement)
- **SQuAD v2.0:** 83.1 F1 / 80.0 EM (5.1+ F1 improvement)
- **MultiNLI:** 86.7% accuracy (4.6% improvement)
- **SWAG:** 86.3% accuracy (1.5% improvement)

BERT achieved SOTA on all major NLP benchmarks at the time of publication.

## Why It Matters

BERT revolutionized NLP by demonstrating:

1. **Pre-training + fine-tuning paradigm is extremely effective** - One pre-trained model can be adapted to many tasks
2. **Bidirectional context matters** - Significantly better than unidirectional approaches
3. **Transfer learning works for NLP** - Similar to how computer vision uses pre-trained models

BERT led to a Cambrian explosion of Transformer-based language models and established the pre-train/fine-tune paradigm that dominated NLP for years.

## Weaknesses

- **MLM training is slower** - Only 15% of tokens are predicted per batch (vs 100% in next-token prediction)
- **Pre-train/fine-tune discrepancy** - [MASK] token appears during pre-training but not during fine-tuning
- **NSP task is less useful** - Later research showed NSP provides minimal benefit
- **Not generative** - BERT is primarily for understanding, not generation

## Follow-up Work

- **RoBERTa:** Improved pre-training with longer training, more data, removing NSP
- **ALBERT:** Parameter efficiency improvements
- **DistilBERT:** Knowledge distillation for smaller, faster models
- **GPT-2/3:** Showed that autoregressive (unidirectional) models can also be very effective at understanding tasks with enough scale