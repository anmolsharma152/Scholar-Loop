---
topic: papers
difficulty: hard
last_sent:
review_count: 0
tags:
  - paper
  - gpt
  - generative-pretraining
  - transfer-learning
  - transformer
  - nlp
  - language-model
---

# Improving Language Understanding by Generative Pre-Training (GPT-1)

**Authors:** Alec Radford, Karthik Narasimhan, Tim Salimans, Ilya Sutskever (OpenAI)
**Published:** OpenAI preprint, June 2018
**arXiv:** N/A - not on arXiv

## Problem & Motivation

Most deep learning methods require substantial amounts of manually labeled data, restricting applicability in domains with scarce annotations. Leveraging more than word-level information from unlabeled text is challenging: there is no consensus on the most effective pre-training objective (language modeling, machine translation, discourse coherence each outperform others on different tasks), and no agreement on the best way to transfer learned representations to downstream tasks. Previous approaches involved task-specific architecture modifications, intricate learning schemes, or auxiliary objectives. The goal was to learn a universal representation that transfers with minimal adaptation to a wide range of natural language understanding tasks.

## Key Idea / Architecture

### Two-Stage Training

**Stage 1: Unsupervised pre-training.** Maximize standard language modeling objective: L1(U) = sum_i log P(u_i | u_{i-k}, ..., u_{i-1}; theta) on the BooksCorpus dataset (7,000+ unpublished books with long contiguous text spans including Adventure, Fantasy, Romance). The model achieves perplexity 18.4 on this corpus.

**Stage 2: Supervized fine-tuning.** Adapt pre-trained parameters to labeled tasks using P(y|x1,...,xm) = softmax(h_l * Wy). An auxiliary language modeling loss L3(C) = L2(C) + lambda * L1(C) with lambda=0.5 is added during fine-tuning to improve generalization and accelerate convergence.

### Architecture

12-layer decoder-only transformer with masked self-attention heads: 768 hidden states, 12 attention heads, 3072 inner states for position-wise FFNs. Uses GELU activation, learned position embeddings (not sinusoidal), BPE vocabulary with 40,000 merges. Dropout 0.1, modified L2 regularization (w=0.01). Adam optimizer with max learning rate 2.5e-4 (linear warmup over first 2000 updates, cosine decay to 0). Trained 100 epochs on minibatches of 64 sequences of 512 tokens.

### Task-Specific Input Transformations

For entailment: premise + delimiter ($) + hypothesis. For similarity: both orderings processed independently then element-wise summed (since no inherent ordering). For QA/commonsense: context + question + delimiter + each answer processed separately then softmax-normalized. All transformations include randomly initialized start and end tokens.

## Key Contributions

1. First demonstration that generative pre-training of transformers followed by discriminative fine-tuning yields strong NLP transfer across diverse tasks
2. Task-aware input transformations requiring minimal architectural changes during transfer
3. State-of-the-art results on 9 of 12 NLP tasks studied
4. Established the pre-train + fine-tune paradigm that became the foundation of modern NLP

## Results (Specific Numbers)

### Natural Language Inference

| Dataset | GPT-1 | Previous Best |
|---------|-------|--------------|
| MNLI-m | 82.1% | CAFE 78.7% |
| MNLI-mm | 81.4% | CAFE 77.9% |
| SNLI | 89.9% | GenSen 82.3% |
| SciTail | 88.3% | CAFE 83.3% (+5.0%) |
| QNLI | 88.1% | BiLSTM 82.1% (+5.8%) |
| RTE | 56.0% | BiLSTM 61.7% |

### Question Answering and Commonsense

| Task | GPT-1 | Previous Best |
|------|-------|--------------|
| Story Cloze Test | 86.5% | 59.0% (+8.9% absolute) |
| RACE (combined) | 59.0% | — (+5.7%) |

### Semantic Similarity and Classification

| Task | GPT-1 | Previous Best |
|------|-------|--------------|
| STS-B (Pearson) | 82.0% | 72.8% (+1 point) |
| QQP (F1) | 70.3% | 66.1% |
| CoLA (Matthews) | 45.4 | 35.0 |
| SST-2 | 91.3% | 90.2% |
| GLUE overall | 72.8 | 68.9 |

### Key Ablations

- Transferring all 12 layers improves performance up to 9% on MultiNLI vs transferring only embeddings
- Auxiliary LM objective during fine-tuning improves results and accelerates convergence
- BooksCorpus (contiguous text) outperforms 1B Word Benchmark (shuffled sentences) for pre-training

## Why It Matters / Impact

GPT-1 established the generative pre-training + discriminative fine-tuning paradigm that became the foundation of modern NLP. The insight that a single language model pre-trained on diverse text could transfer to many tasks with minimal modification led directly to GPT-2, GPT-3, BERT, and the entire modern LLM ecosystem. The paper demonstrated that scaling pre-training data and model capacity together yields broad capability gains, validating the importance of unsupervised learning for NLP.

## Weaknesses / Limitations

- RTE results (56%) below previous SOTA (61.7%), suggesting the approach benefits from more data or multi-task training
- Limited to classification-like tasks; does not generate text for generation tasks
- BooksCorpus is a specific domain; generalization to other pretraining corpora not explored
- Only 12-layer model; does not explore scaling laws that later GPT versions investigated
- Bidirectional models (like BERT, released same year) would outperform GPT-1 on understanding tasks
- Requires task-specific input transformations rather than a truly uniform interface

## Follow-up Work / Key References

- GPT-2 (Radford et al., 2019) — scaled to 1.5B parameters, demonstrated zero-shot task transfer
- GPT-3 (Brown et al., 2020) — 175B parameters, in-context learning, few-shot prompting
- BERT (Devlin et al., 2018) — bidirectional pre-training, outperformed GPT-1 on understanding tasks
- RoBERTa (Liu et al., 2019) — optimized BERT pre-training, achieved better GLUE scores
- Howard and Ruder (2018) ULMFiT — earlier LSTM-based pre-train + fine-tune for text classification
