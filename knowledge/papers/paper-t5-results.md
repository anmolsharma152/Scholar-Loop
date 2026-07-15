---
topic: papers
difficulty: hard
last_sent:
review_count: 0
tags:
  - paper
  - transfer-learning
  - text-to-text
  - results
---

# T5: Results, Impact & Limitations

**Authors:** Colin Raffel, Noam Shazeer, Adam Roberts, et al. (Google)
**Published:** JMLR 2020 (arXiv 1910.10683)

## Results

- Baseline GLUE score: 83.28 (vs. 66.22 without pre-training)
- Baseline SuperGLUE: 71.36 (vs. 53.04 without pre-training)
- Baseline SQuAD EM: 80.88 (vs. 50.31 without pre-training)
- Encoder-decoder denoising outperforms language modeling by ~3-4 points on GLUE and SuperGLUE
- Architecture: encoder-decoder 84.3 vs. language model 81.2 vs. prefix language model 82.0 (GLUE avg)
- Scaling: Small (60M) → Base (220M) → Large (770M) → 3B → 11B, GLUE: 78.2 → 83.3 → 86.1 → 89.0 → 91.2
- C4 dataset size impact: 750 GB after filtering yields best quality vs. unfiltered Common Crawl (83.3 vs. 81.8 GLUE)
- Span length of 3 is optimal: GLUE 83.3 (span 3) vs. 82.8 (span 2) vs. 82.1 (span 5) vs. 81.2 (span 10)

## Why It Matters

T5 established a new paradigm for unifying NLP under a single text-to-text framework, simplifying the design and evaluation of transfer learning. The C4 dataset became widely used as a pre-training corpus. The systematic empirical study provided clear guidance for practitioners: use encoder-decoder architecture, denoising pre-training objectives, and scale up.

## Weaknesses / Limitations

1. The text-to-text format can be inefficient for tasks where structured output formats would be more natural
2. The baseline is pre-trained on only ~34B tokens, far less than BERT (137B) or RoBERTa (2.2T)
3. The study does not explore all combinations of factors (coordinate-ascent approach may miss second-order interactions)
4. The C4 dataset is English-only and filtered with heuristics that may discard useful content
5. The encoder-decoder architecture roughly doubles parameter count compared to encoder-only models

## Follow-up Work

- **T5 variants** (mT5, Flan-T5): Extensions to multilingual and instruction-tuned settings
- **GShard & Switch Transformers:** MoE layers replacing T5 FFN for scaling to trillions of parameters
- **C4 dataset adoption:** Used as standard pre-training corpus by GPT-NeoX, UL2, and many others
- **UL2:** Unified language learning that generalizes the T5 denoising framework with multiple objective modes
- **SentenceT5:** Sentence-level encoder variant for better sentence embeddings
