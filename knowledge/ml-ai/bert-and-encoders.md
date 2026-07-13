---
difficulty: medium
last_sent: null
review_count: 0
tags:
- bert
- encoder
- nlp
topic: ml-ai
---

# BERT and Encoder Models

BERT (Bidirectional Encoder Representations from Transformers, Devlin et al. 2018) revolutionized NLP by introducing a **pre-train then fine-tune** paradigm using only the encoder stack of the Transformer. Unlike GPT (unidirectional), BERT reads the entire input in both directions simultaneously, giving it deep contextual understanding for classification, NER, QA, and other understanding tasks.

## Encoder-Only Architecture

BERT uses only the **encoder** portion of the Transformer — no cross-attention, no causal masking. Every token can attend to every other token freely. This makes it ideal for tasks where you need to understand the full input at once (classification, extraction, similarity) rather than generate text token by token.

The architecture is straightforward: token embeddings + positional embeddings + segment embeddings are summed, then passed through N stacked Transformer encoder layers (12 for BERT-Base, 24 for BERT-Large).

```python
import torch
import torch.nn as nn

class BERTEmbedding(nn.Module):
    def __init__(self, vocab_size, d_model, max_len, num_segments=2):
        super().__init__()
        self.token = nn.Embedding(vocab_size, d_model)
        self.position = nn.Embedding(max_len, d_model)
        self.segment = nn.Embedding(num_segments, d_model)
        self.norm = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(0.1)

    def forward(self, input_ids, segment_ids):
        seq_len = input_ids.size(1)
        positions = torch.arange(seq_len, device=input_ids.device).unsqueeze(0)
        x = self.token(input_ids) + self.position(positions) + self.segment(segment_ids)
        return self.dropout(self.norm(x))
```

## Masked Language Modeling (MLM)

BERT's primary pre-training objective. During training, **15% of input tokens are randomly selected**, and of those:

- 80% are replaced with `[MASK]`
- 10% are replaced with a random token
- 10% are kept unchanged

The model must predict the original token at each masked position using cross-entropy loss. The 80/10/10 split prevents a mismatch between pre-training (always `[MASK]`) and fine-tuning (never `[MASK]`).

```python
def create_mlm_batch(input_ids, vocab_size, mask_token_id, mask_prob=0.15):
    labels = input_ids.clone()
    mask = torch.rand(input_ids.shape) < mask_prob

    # 80% mask, 10% random, 10% keep
    replace_mask = torch.rand(input_ids.shape) < 0.8
    random_mask = (torch.rand(input_ids.shape) < 0.1) & ~replace_mask

    input_ids[mask & replace_mask] = mask_token_id
    input_ids[mask & random_mask] = torch.randint(0, vocab_size, input_ids[mask & random_mask].shape)
    labels[~mask] = -100  # ignore non-masked positions in loss
    return input_ids, labels
```

## Next Sentence Prediction (NSP)

BERT's secondary pre-training objective. Given sentence A and sentence B, the model predicts whether B actually follows A in the original text (50% positive, 50% negative pairs). The `[CLS]` token's final representation is used for this binary classification.

NSP was later found to be less important than MLM — RoBERTa showed better results by removing it entirely. However, it remains part of the original BERT formulation and is tested in exams/interviews.

## The [CLS] Token

BERT prepends a special `[CLS]` token to every input. Its final hidden state is used as the aggregate sequence representation for classification tasks. During pre-training, `[CLS]` is used for NSP. During fine-tuning, you add a simple linear layer on top of the `[CLS]` output.

```python
class BERTForClassification(nn.Module):
    def __init__(self, bert_encoder, num_classes, d_model=768):
        super().__init__()
        self.bert = bert_encoder
        self.classifier = nn.Linear(d_model, num_classes)

    def forward(self, input_ids, attention_mask, segment_ids):
        outputs = self.bert(input_ids, attention_mask, segment_ids)
        cls_output = outputs[:, 0, :]  # [CLS] token is at position 0
        return self.classifier(cls_output)
```

## Bidirectional Context

The key difference from GPT: BERT sees the full context in both directions. When predicting a masked word like "The [MASK] sat on the mat", BERT sees both "The" (left context) and "sat on the mat" (right context). This bidirectional view is crucial for understanding tasks but **precludes autoregressive generation** — you cannot generate text token-by-token with a model that expects to see the full sequence.

| Model | Direction | Pre-training | Best for |
|-------|-----------|-------------|----------|
| BERT | Bidirectional | MLM + NSP | Classification, NER, QA |
| GPT | Left-to-right | Next token prediction | Generation, few-shot learning |
| T5 | Encoder-decoder | Span corruption | Seq2seq tasks |

## BERT Variants

| Model | Key change | Impact |
|-------|-----------|--------|
| RoBERTa | Remove NSP, more data, dynamic masking | Better across the board |
| ALBERT | Factorized embeddings, parameter sharing | Fewer parameters, same performance |
| DistilBERT | Knowledge distillation from BERT | 60% smaller, 97% performance |
| DeBERTa | Disentangled attention (content + position) | State-of-the-art on SuperGLUE |

## Key takeaways

- BERT is an encoder-only model: no generation, only understanding
- MLM pre-training teaches deep bidirectional representations
- `[CLS]` token is the gateway for sequence-level tasks
- BERT was a turning point: pre-train on massive data, fine-tune on task-specific data with minimal architecture changes
- RoBERTa essentially supersedes vanilla BERT for most uses

## Common bugs

- Using `[MASK]` token during fine-tuning (it only appears during pre-training; never feed it at inference)
- Forgetting to set `segment_ids` to 0 for single-segment tasks (some implementations expect explicit zeros)
- Not using attention masking for padding — `[CLS]` representation gets corrupted by padding attenders
- Confusing the MLM loss positions: labels must be `-100` for non-masked tokens to ignore them in `CrossEntropyLoss`
- Assuming BERT can generate text autoregressively — it cannot, use GPT-style models for generation
