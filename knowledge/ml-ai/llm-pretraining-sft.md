---
difficulty: hard
last_sent: null
review_count: 0
tags:
- llm
- pretraining
- sft
topic: ml-ai
---

# LLM Pre-Training & SFT

## Stage 1: Pre-Training

The foundation. A transformer decoder is trained on trillions of tokens using **next-token prediction** (cross-entropy loss). The model learns language structure, world knowledge, reasoning patterns, and some task abilities — all from raw text.

```python
import torch
import torch.nn.functional as F

def pretraining_loss(model, input_ids):
    logits = model(input_ids[:, :-1])        # (batch, seq_len-1, vocab)
    targets = input_ids[:, 1:]                # (batch, seq_len-1)
    loss = F.cross_entropy(
        logits.reshape(-1, logits.size(-1)),
        targets.reshape(-1),
        ignore_index=-100  # padding tokens
    )
    return loss
```

Key pre-training details:
- **Data**: Mix of web text, books, code, scientific papers (e.g., Common Crawl, The Pile, RedPajama)
- **Objective**: Cross-entropy on next token — simple but scales remarkably well
- **Schedule**: Cosine learning rate decay with warmup (typically 2000 steps)
- **Batch size**: Millions of tokens per batch (gradient accumulation over micro-batches)
- **Compute**: Thousands of GPU-hours on A100/H100 clusters

## Stage 2: Supervised Fine-Tuning (SFT)

Takes the pre-trained model and teaches it to follow instructions. Trained on **(instruction, response)** pairs where human annotators write high-quality answers.

```python
def sft_loss(model, input_ids, labels):
    logits = model(input_ids)
    loss = F.cross_entropy(
        logits.reshape(-1, logits.size(-1)),
        labels.reshape(-1),
        ignore_index=-100  # mask instruction tokens
    )
    return loss
```

SFT typically uses:
- **High-quality curated data**: 10K-100K instruction-response pairs
- **Loss masking**: Only compute loss on response tokens, not the instruction
- **Low learning rate**: 1e-5 to 5e-5 (smaller than pre-training)
- **Short epochs**: 1-5 epochs (avoid overfitting on small dataset)

The goal of SFT is not to teach new knowledge but to teach the model the **format** and **style** of a helpful assistant.

## Key Takeaways

- Pre-training teaches knowledge and reasoning; SFT teaches format
- Data quality matters more than quantity at every stage — 10K high-quality SFT examples often beat 1M mediocre ones
- Pre-training compute dominates the total pipeline (95%+ of total cost)
