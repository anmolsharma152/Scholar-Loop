---
difficulty: hard
last_sent: null
review_count: 0
tags:
- llm
- rlhf
- dpo
- alignment
topic: ml-ai
---

# LLM Alignment: RLHF & DPO

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
        self.reward_head = nn.Linear(d_model, 1)

    def forward(self, input_ids):
        hidden = self.model(input_ids).last_hidden_state
        reward = self.reward_head(hidden[:, -1, :])
        return reward.squeeze(-1)

def reward_loss(chosen_reward, rejected_reward):
    return -torch.mean(torch.log(torch.sigmoid(chosen_reward - rejected_reward)))
```

## Stage 3b: RLHF — PPO Optimization

With the reward model frozen, the SFT model is fine-tuned using **PPO** to maximize the reward model's score while staying close to the SFT model.

```
reward = RM(response) - β × KL(π_θ || π_ref)
```

Where `π_θ` is the policy being optimized, `π_ref` is the frozen SFT model, and `β` controls the KL penalty. Without the KL term, the model "hacks" the reward model by producing degenerate outputs.

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

Where `y_w` is the preferred response and `y_l` is the dispreferred response.

```python
def dpo_loss(policy, reference, chosen_ids, rejected_ids, beta=0.1):
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

- **Helpful**: Answer the user's question accurately and completely
- **Harmless**: Refuse to generate dangerous, illegal, or toxic content
- **Honest**: Say "I don't know" when uncertain, avoid hallucination

These objectives often conflict — being too safe makes the model unhelpful, being too helpful can be unsafe.

## Common Bugs

- Computing SFT loss on instruction tokens instead of response tokens
- Forgetting to freeze the reward model during PPO
- Setting KL penalty (β) too low — model hacks reward model
- Setting KL penalty (β) too high — model barely changes from SFT baseline
- Mixing up chosen and rejected labels in DPO — reverses the learning signal
