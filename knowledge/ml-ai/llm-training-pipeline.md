---
difficulty: hard
last_sent: null
review_count: 0
tags:
- llm
- training
- rlhf
- alignment
topic: ml-ai
---

# LLM Training Pipeline

Modern large language models follow a multi-stage training pipeline: **pre-training** on massive text corpora, **supervised fine-tuning (SFT)** on instruction-following data, and **alignment** via RLHF or DPO to make outputs helpful, harmless, and honest. Each stage builds on the previous, progressively narrowing the model from a raw text predictor to a useful assistant.

## Stage 1: Pre-Training

The foundation. A transformer decoder is trained on trillions of tokens using **next-token prediction** (cross-entropy loss). The model learns language structure, world knowledge, reasoning patterns, and some task abilities — all from raw text.

```python
import torch
import torch.nn.functional as F

def pretraining_loss(model, input_ids):
    # Shift: predict next token from previous tokens
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
# SFT training example
# Input: "What is photosynthesis? \n\n" + "Photosynthesis is the process by which..."
# Only the response tokens contribute to the loss
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

## Stage 3: RLHF — Reward Modeling

After SFT, the model is further aligned using Reinforcement Learning from Human Feedback (RLHF). First, a **reward model** is trained on human preference data:

1. Generate multiple responses to the same prompt
2. Human annotators rank them from best to worst
3. Train a reward model to predict these preferences

```python
class RewardModel(nn.Module):
    def __init__(self, base_model, d_model):
        super().__init__()
        self.model = base_model
        self.reward_head = nn.Linear(d_model, 1)  # scalar reward

    def forward(self, input_ids):
        hidden = self.model(input_ids).last_hidden_state
        # Use the last non-padding token's representation
        reward = self.reward_head(hidden[:, -1, :])
        return reward.squeeze(-1)

def reward_loss(chosen_reward, rejected_reward):
    # Chosen response should score higher than rejected
    return -torch.mean(torch.log(torch.sigmoid(chosen_reward - rejected_reward)))
```

## Stage 3b: RLHF — PPO Optimization

With the reward model frozen, the SFT model is fine-tuned using **PPO (Proximal Policy Optimization)** to maximize the reward model's score while staying close to the SFT model (to avoid degeneration).

The RLHF objective combines:

```
reward = RM(response) - β × KL(π_θ || π_ref)
```

Where `π_θ` is the policy being optimized, `π_ref` is the frozen SFT model, and `β` controls the KL penalty. Without the KL term, the model "hacks" the reward model by producing degenerate outputs that maximize score but are nonsensical.

```python
def ppo_loss(policy_logprobs, old_logprobs, advantages, clip_range=0.2):
    ratio = torch.exp(policy_logprobs - old_logprobs)
    clipped = torch.clamp(ratio, 1 - clip_range, 1 + clip_range)
    return -torch.min(ratio * advantages, clipped * advantages).mean()
```

PPO details:
- Requires 4 models simultaneously: policy, reference policy, reward model, value head
- Very memory-intensive and complex to implement
- Requires careful hyperparameter tuning (β, clip range, batch size, epochs)

## Stage 3c: DPO — Direct Preference Optimization

DPO (Rafailov et al., 2023) eliminates the need for a separate reward model and RL training. It reformulates the RLHF objective as a simple classification loss on preference pairs:

```
L_DPO = -log σ(β × [log π_θ(y_w|x)/π_ref(y_w|x) - log π_θ(y_l|x)/π_ref(y_l|x)])
```

Where `y_w` is the preferred (chosen) response and `y_l` is the dispreferred (rejected) response. This is essentially a binary cross-entropy loss — much simpler to implement and more stable to train.

```python
def dpo_loss(policy, reference, chosen_ids, rejected_ids, beta=0.1):
    # Log probabilities under policy and reference
    policy_chosen_logprobs = compute_logprobs(policy, chosen_ids)
    policy_rejected_logprobs = compute_logprobs(policy, rejected_ids)
    ref_chosen_logprobs = compute_logprobs(reference, chosen_ids)
    ref_rejected_logprobs = compute_logprobs(reference, rejected_ids)

    chosen_rewards = beta * (policy_chosen_logprobs - ref_chosen_logprobs)
    rejected_rewards = beta * (policy_rejected_logprobs - ref_rejected_logprobs)

    return -F.logsigmoid(chosen_rewards - rejected_rewards).mean()
```

DPO advantages: no reward model, no RL loop, no value head, simpler to implement, more stable training.

## Alignment Goals

The purpose of alignment is to make models:

- **Helpful**: Answer the user's question accurately and completely
- **Harmless**: Refuse to generate dangerous, illegal, or toxic content
- **Honest**: Say "I don't know" when uncertain, avoid hallucination

These objectives often conflict — being too safe makes the model unhelpful, being too helpful can be unsafe. The art of alignment is finding the right balance.

## The Full Pipeline

```
Raw Text → Pre-training (next token) → SFT (instructions) → Alignment (RLHF/DPO)
  │              │                          │                        │
  │              │                          │                        │
  ▼              ▼                          ▼                        ▼
GPT base     Foundation                Chat model              Aligned model
(autoregressive   model              (follows instructions)   (helpful, safe)
 predictor)
```

## Key takeaways

- Pre-training teaches knowledge and reasoning; SFT teaches format; alignment teaches values
- The KL penalty in RLHF is critical — without it, the model collapses to reward hacking
- DPO is replacing RLHF in many settings due to simplicity and comparable performance
- Data quality matters more than quantity at every stage — 10K high-quality SFT examples often beat 1M mediocre ones
- Pre-training compute dominates the total pipeline (95%+ of total cost)
- Recent trends: Constitutional AI (self-supervised alignment), iterative DPO, online RLHF

## Common bugs

- Computing SFT loss on instruction tokens instead of response tokens — teaches the model to predict instructions
- Forgetting to freeze the reward model during PPO — causes reward model to collapse
- Setting KL penalty (β) too low — model hacks reward model with degenerate outputs
- Setting KL penalty (β) too high — model barely changes from SFT baseline
- Using greedy decoding during RLHF generation — reduces diversity, hurts exploration
- Not using the same tokenizer/data preprocessing for SFT and DPO — causes distribution mismatch
- Mixing up chosen and rejected labels in DPO — reverses the learning signal entirely
- Training DPO with too large a learning rate — policy diverges from reference model quickly
