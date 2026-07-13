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
  - nlp
---

# Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer

**Authors:** Colin Raffel, Noam Shazeer, Adam Roberts, Katherine Lee, Sharan Narang, Michael Matena, Yanqi Zhou, Wei Li, Peter J. Liu (Google)
**Published:** Journal of Machine Learning Research 21 (2020)
**arXiv:** 1910.10683

## Problem & Motivation

The landscape of transfer learning for NLP had grown fragmented, with a diversity of pre-training objectives, architectures, unlabeled datasets, and transfer approaches making it difficult to compare methods and understand the space. Prior work used different task-specific heads and objectives (classification, span extraction, language modeling), preventing a unified empirical study. The field needed a comprehensive, controlled comparison across dozens of factors to understand what matters most and to push the limits of transfer learning through scale.

## Key Idea / Architecture

T5 unifies all text-based language problems into a single "text-to-text" format where every task takes text as input and produces text as output. For classification, the model outputs a single label word; for translation, it generates the translated sentence; for summarization, it produces the summary. A task-specific text prefix (e.g., "translate English to German:", "mnli premise:... hypothesis:...") specifies which task to perform, allowing the same model, objective, training procedure, and decoding process across all tasks.

The base architecture is an encoder-decoder Transformer closely following the original Vaswani et al. design, with key modifications: simplified layer normalization (no additive bias, placed outside the residual path), and relative position embeddings as scalars added to attention logits (32 learned embeddings with logarithmic ranges up to offset 128, shared across layers).

The "Colossal Clean Crawled Corpus" (C4) is introduced—a 750 GB dataset of clean English text from Common Crawl (April 2019). Filtering heuristics include: retaining only lines ending in terminal punctuation, discarding pages with fewer than 3 sentences, removing pages with offensive words, JavaScript references, lorem ipsum, curly brackets (code), citation markers, and boilerplate. Three-sentence span deduplication is applied, and langdetect filters non-English pages (probability ≥ 0.99).

The baseline uses a denoising objective that randomly samples and drops out 15% of tokens, replacing consecutive dropped spans with unique sentinel tokens. The target consists of the dropped spans delimited by the same sentinels plus a final sentinel. This outperforms standard language modeling, BERT-style masked LM, and other pre-training objectives. The baseline model has 220M parameters (roughly 2× BERT-base due to encoder+decoder), is pre-trained for 2^19 = 524,288 steps on C4 (~34B tokens), uses AdaFactor optimizer with inverse square root learning rate schedule (warmup of 10^4 steps), sequence length 512, and batch size 128 sequences.

Scaling experiments train models up to 11 billion parameters on Cloud TPU Pods using Mesh TensorFlow for model and data parallelism. Architecture comparisons test encoder-decoder vs. language model vs. prefix LM, finding encoder-decoder with denoising consistently best. The denoising objective always outperforms language modeling across all architectures. Sharing encoder-decoder parameters performs nearly as well as the full model while halving parameters.

## Key Contributions

1. Unified text-to-text framework casting every NLP task as text-to-text, enabling consistent comparison across dozens of tasks and experimental factors.
2. The Colossal Clean Crawled Corpus (C4), a large-scale cleaned dataset from Common Crawl, released as part of TensorFlow Datasets.
3. Comprehensive empirical study comparing pre-training objectives (denoising best), architectures (encoder-decoder best), datasets, and transfer approaches.
4. State-of-the-art results on many benchmarks by combining insights from the systematic study with scale (models up to 11B parameters).

## Results (Specific Numbers)

- Baseline GLUE score: 83.28 (vs. 66.22 without pre-training)
- Baseline SuperGLUE: 71.36 (vs. 53.04 without pre-training)
- Baseline SQuAD EM: 80.88 (vs. 50.31 without pre-training)
- Baseline CNN/Daily Mail R-2-F: 19.24
- Baseline En-De BLEU: 26.98, En-Fr BLEU: 39.82, En-Ro BLEU: 27.65
- Encoder-decoder denoising outperforms language modeling by ~3-4 points on GLUE and SuperGLUE
- The largest T5 (11B) achieves state-of-the-art on numerous benchmarks at time of publication
- Pre-training objective comparison: denoising 84.3 GLUE vs. language modeling 80.1 vs. span corruption 82.7
- Architecture: encoder-decoder 84.3 vs. language model 81.2 vs. prefix language model 82.0 (GLUE avg)
- Scaling ablation: Small (60M) → Base (220M) → Large (770M) → 3B → 11B, GLUE: 78.2 → 83.3 → 86.1 → 89.0 → 91.2
- C4 dataset size impact: 750 GB after filtering yields best quality vs. unfiltered Common Crawl (83.3 vs. 81.8 GLUE)
- Sentinels used for denoising: adding sentinel tokens improves GLUE by ~0.5 points vs. simple dropped-span replacement
- Span length of 3 is optimal: GLUE 83.3 (span 3) vs. 82.8 (span 2) vs. 82.1 (span 5) vs. 81.2 (span 10)

## Why It Matters / Impact

T5 established a new paradigm for unifying NLP under a single text-to-text framework, simplifying the design and evaluation of transfer learning. The C4 dataset became widely used as a pre-training corpus. The systematic empirical study provided clear guidance for practitioners: use encoder-decoder architecture, denoising pre-training objectives, and scale up. The released models, code, and data facilitated a large body of follow-up work and became a standard reference point in NLP research.

## Weaknesses / Limitations

1. The text-to-text format can be inefficient for tasks where structured output formats (span extraction) would be more natural, adding unnecessary generation overhead.
2. The baseline is pre-trained on only ~34B tokens, far less than BERT (137B) or RoBERTa (2.2T), making some comparisons not fully equitable.
3. The study does not explore all combinations of factors (coordinate-ascent approach may miss second-order interactions between factors).
4. The C4 dataset is English-only and filtered with heuristics that may discard useful content while retaining noise.
5. The encoder-decoder architecture roughly doubles parameter count compared to encoder-only models at equivalent computational cost, complicating fair comparisons.

## Follow-up Work

- T5 variants (mT5, Flan-T5): Extensions to multilingual and instruction-tuned settings.
- GShard & Switch Transformers: MoE layers replacing T5 FFN for scaling to trillions of parameters.
- C4 dataset adoption: Used as standard pre-training corpus by GPT-NeoX, UL2, and many others.
- UL2: Unified language learning that generalizes the T5 denoising framework with multiple objective modes.
- C4-300B: Subset of C4 used by PaLM (300B tokens) for comparison purposes.
- mT5 (Xue et al., 2021): Extension to 101 languages using the same text-to-text paradigm with mC4 corpus.
- T5 v1.1: Improved baseline with longer training (2^21 steps) achieving GLUE 85.2 and SuperGLUE 74.8
- SentenceT5: Sentence-level encoder variant for better sentence embeddings on semantic similarity tasks
