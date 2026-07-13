---
topic: papers
difficulty: medium
last_sent:
review_count: 0
tags:
  - paper
  - survey
  - BERT
  - NLP
  - transformers
---

# A Survey on BERT and Its Applications

**Authors:** Sulaiman Aftan (Texas Tech University), Habib Shah (King Khalid University)
**Published:** 20th Learning and Technology Conference (IEEE) 2023
**arXiv:** N/A

## Problem & Motivation

BERT (Bidirectional Encoder Representations from Transformers) achieved excellent results across many NLP tasks since its introduction in 2018, spawning numerous variants with different specializations. However, a comprehensive survey of these variants and their applications across diverse fields was needed. The authors wanted to catalog the landscape of BERT derivatives, compare their innovations and results, and identify gaps and future research directions across computer science, engineering, medicine, and social science applications. The survey covers over 36 references and spans multiple application domains from fake news detection to food entity recognition. Since BERT's original release, dozens of variants have been proposed, each targeting different optimization strategies or domain applications.

## Key Idea / Architecture

BERT is a bidirectional deep learning model that analyzes text by attending to both left and right contexts simultaneously, unlike unidirectional models. It uses the Transformer encoder architecture and follows a two-phase approach: pre-training on unlabeled text (using masked language modeling and next sentence prediction objectives) and fine-tuning on labeled task-specific data. The [CLS] token at the beginning of input serves as the aggregate representation for classification tasks, while individual token representations are used for token-level tasks.

The survey covers major BERT variants including: RoBERTa (Robustly Optimized BERT Approach), which removes the next sentence prediction objective and uses dynamic masking for better performance; ALBERT (A Lite BERT), which reduces parameters through factorized embedding parameterization and cross-layer parameter sharing; DistilBERT, a distilled version retaining 97% of BERT's performance while being 60% faster; ELECTRA, which uses a replaced token detection pre-training task for better sample efficiency; SpanBERT, which extends BERT by masking contiguous random spans rather than individual tokens; BioBERT, pre-trained on biomedical text corpora; ClinicalBERT, for clinical notes; AraBERT, for Arabic text; and Multi-lingual BERT (mBERT).

```
BERT input: [CLS] + Token_1 + ... + Token_n + [SEP]
Pre-training objectives: Masked LM (predict masked tokens) + Next Sentence Prediction
Fine-tuning: Add task-specific head and train on labeled data
```

## Key Contributions

1. Comprehensive catalog of BERT variants: RoBERTa, ALBERT, DistilBERT, ELECTRA, SpanBERT, BioBERT, ClinicalBERT, AraBERT, and their specific innovations
2. Surveyed applications across diverse domains: NLP classification, fake news detection, food entity recognition, medical diagnosis, sentiment analysis, knowledge graph completion, and recommendation systems
3. Documented specific performance results: BERT achieved >4.6% and >7.7% accuracy improvement on 11 NLP tasks for base and large variants respectively
4. Found fake news detection with BERT achieved F-score 99.15%, precision 98.86%, recall 99.46%, far surpassing traditional ML and DL methods
5. Surveyed 36+ BERT applications across NLP, medical, biological, and social media domains
6. Highlighted future directions including hybridization with metaheuristic algorithms, hybridization with computational intelligence, and extension to non-English languages

## Results (Specific Numbers)

- BERT Base/Large: 4.6%/7.7% absolute improvement on 11 NLP tasks (original paper)
- RoBERTa: outperformed standard BERT on sentiment classification (80/20 train/test split)
- BioBERT: 93-94% macro F1 for food entity recognition (75/25 split)
- DistilBERT: 97% of BERT performance, 60% faster, 40% smaller
- Fake news detection: F-score 99.15%, precision 98.86%, recall 99.46%
- AlBERTo (Italian social media): exceptional F1 score and precision on Italian text
- X-BERT: superior results on Eurlex-4K, Wiki10-28K, AmazonCat-13K for extreme multi-label classification
- BERT4Rec: successful sequential recommendation on Beauty, Steam, ML-1m, ML-20m datasets
- Dialog State Tracking: BERT achieved 7x faster and 8x smaller than previous models on WoZ 2.0 dataset

## Why It Matters / Impact

BERT fundamentally changed the NLP landscape by demonstrating the power of bidirectional pre-training followed by task-specific fine-tuning. This paradigm shift spawned an entire ecosystem of specialized models for different domains and languages. The survey documents how BERT variants became the default approach across virtually all NLP tasks, replacing earlier RNN/LSTM-based methods. The proliferation of domain-specific variants (BioBERT, ClinicalBERT, LegalBERT) showed that pre-training on domain-relevant corpora consistently improves downstream performance, establishing a template that continues to influence model development. BERT's success also validated the pre-train/fine-tune paradigm that underpins all modern large language models. The variety of optimization strategies explored across variants—distillation, factorization, robust training—established a rich toolkit for model compression and adaptation.

## Weaknesses / Limitations

- The survey primarily covers applications up to 2023 and does not address post-BERT developments (GPT-3, instruction-tuned models, etc.)
- Limited quantitative comparison across variants—most results are reported for individual variants on individual tasks rather than systematic head-to-head benchmarks
- No discussion of computational costs, training requirements, or practical deployment considerations for any of the BERT variants
- Focuses heavily on English and NLP tasks, with limited coverage of multimodal or cross-lingual applications
- Does not address fundamental limitations of BERT-style architectures (context length limits, quadratic attention complexity, etc.)
- The survey lacks a systematic methodology for selecting and comparing the included papers and variants
- Many application-specific BERT variants (BioBERT, ClinicalBERT, etc.) may not outperform general fine-tuned BERT in all settings
- Results are reported inconsistently across papers, using different metrics, datasets, and evaluation protocols
- The survey was published at IEEE L&T 2023 conference, not a top NLP venue, limiting peer review rigor

## Follow-up Work

- RoBERTa-DeBERTa: combining robust pre-training with disentangled attention for improved performance
- Longformer/BigBird: extending BERT's attention mechanism to handle longer documents
- BioBERT/DNA-BERT: domain-specific variants for biomedical and genomic text
- Sentence-BERT: optimizing BERT for semantic similarity tasks with siamese networks

---
