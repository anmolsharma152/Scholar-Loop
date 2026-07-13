---
difficulty: hard
last_sent:
review_count: 0
tags:
  - rlhf
  - alignment
  - llm
topic: ml-ai
---

# RLHF and Alignment

Reinforcement Learning from Human Feedback (RLHF) is the technique that transforms a pre-trained language model into a helpful, harmless assistant by aligning its behavior with human preferences. It is the core training methodology behind ChatGPT, Claude, and other aligned LLMs.

## The Alignment Problem

Pre-training teaches language models to predict the next token, but this objective doesn't guarantee helpfulness, safety, or honesty. A model trained on internet text will learn to produce toxic content, hallucinate, and follow harmful instructions. RLHF bridges this gap by using human preferences as a training signal.

## RLHF Pipeline (3 Stages)

### Stage 1: Supervised Fine-Tuning (SFT)

Fine-tune the pre-trained LLM on a curated dataset of high-quality (prompt, response) pairs to establish a base of desired behavior. This is the "cold start" that gives the model an initial sense of what good responses look like.

### Stage 2: Reward Model Training

Collect human preference data: for each prompt, generate multiple completions and have humans rank them. Train a reward model $r_\phi(x, y)$ to predict which completion a human would prefer.

$$\mathcal{L}_{RM} = -\mathbb{E}_{(x, y_w, y_l) \sim D} \left[\log \sigma(r_\phi(x, y_w) - r_\phi(x, y_l))\right]$$

where $y_w$ is the preferred completion and $y_l$ is the rejected one. This is a **Bradley-Terry** pairwise ranking model.

### Stage 3: PPO Optimization

Optimize the language model using PPO against the learned reward model:

$$\mathcal{L}_{RLHF} = \mathbb{E}_{x, y \sim \pi_\theta}\left[r_\phi(x, y)\right] - \beta \cdot D_{KL}\left(\pi_\theta(y|x) \| \pi_{\text{ref}}(y|x)\right)$$

The KL penalty prevents the model from deviating too far from the SFT model (avoiding **reward hacking** where the model exploits the reward model's weaknesses).

```python
import torch

def rlhf_loss(policy_log_probs, ref_log_probs, rewards, kl_coef=0.1):
    """PPO objective for RLHF."""
    kl_penalty = kl_coef * (policy_log_probs - ref_log_probs)
    return -(rewards - kl_penalty).mean()
```

## Direct Preference Optimization (DPO)

DPO (Rafailov et al., 2023) eliminates the separate reward model by deriving a closed-form loss directly from preferences:

$$\mathcal{L}_{DPO} = -\mathbb{E}_{(x, y_w, y_l)} \left[\log \sigma\left(\beta \log \frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)}\right)\right]$$

DPO reparameterizes the RLHF objective so that the optimal policy is expressed in terms of the reward function, then optimizes the policy directly.

| Aspect | RLHF (PPO) | DPO |
|--------|------------|-----|
| Reward model | Required | Implicit (not needed) |
| Training complexity | 3 stages, 2 models | 1 stage, simpler |
| Hyperparameters | Many (PPO-specific) | Fewer |
| Online sampling | Yes | No (offline) |
| Scalability | Better for complex alignment | Good for simple preferences |

## Constitutional AI (CAI)

Developed by Anthropic, CAI reduces dependence on human feedback by using a set of principles (a "constitution") for AI self-improvement:

1. The model critiques and revises its own responses based on constitutional principles
2. A smaller set of human feedback is used to train a preference model
3. The model is fine-tuned via RLHF using these AI-generated preferences

This scales alignment because generating AI feedback is cheaper than collecting human feedback for every scenario.

## Alignment Tax

The "alignment tax" is the performance cost of making a model aligned — aligned models may refuse to answer certain questions, provide shorter or less creative responses, or be less knowledgeable on sensitive topics. The goal is to minimize this tax while maintaining safety.

## Reward Hacking and Failure Modes

| Failure | Description | Mitigation |
|---------|-------------|------------|
| Reward hacking | Model exploits reward model artifacts | KL penalty, reward model ensembles |
| Mode collapse | Model produces only one type of response | Diverse training data, entropy bonuses |
| Overoptimization | Reward increases but actual quality drops | Early stopping, reward model scaling |
| Sycophancy | Model tells users what they want to hear | Diverse preference data, red-teaming |
| Jailbreaking | Adversarial prompts bypass safety | Robust training, input filtering |

## Key Takeaways

- RLHF is a 3-stage pipeline: SFT → Reward Model → PPO
- The KL penalty prevents reward hacking by anchoring the policy to the SFT model
- DPO simplifies RLHF by eliminating the reward model, but PPO still dominates for frontier models
- Constitutional AI reduces human feedback requirements through AI self-critique
- Alignment remains an open problem — current methods are necessary but insufficient
- Scaling reward models is critical — small reward models are easily hacked

## Common Bugs

| Bug | Symptom | Fix |
|-----|---------|-----|
| Missing KL penalty | Model generates gibberish (reward hacking) | Add KL term with proper coefficient |
| Reward model overfitting | High RM loss, poor downstream performance | More preference data, regularization |
| Learning rate too high | Training diverges | Use $1e-6$ to $5e-6$ for policy, lower for RM |
| Not freezing reference model | KL computation is wrong | Keep $\pi_{\text{ref}}$ frozen during PPO |
| Using DPO without reference model | Loss is meaningless | Always include $\pi_{\text{ref}}$ in DPO loss |
| Inconsistent preference labels | Poor reward model | Standardize labeling guidelines |
