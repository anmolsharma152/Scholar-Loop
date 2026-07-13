---
topic: papers
difficulty: hard
tags: [paper, instruction-tuning, alignment, human-feedback, rlhf]
---

# Training language models to follow instructions with human feedback

**Authors:** Ouyang et al. (OpenAI)
**Published:** NeurIPS 2022
**arXiv:** 2203.02155

## Problem & Motivation

Large language models like GPT-3 can follow instructions to some extent, but they have several issues:
1. They may generate harmful, unethical, or untruthful content
2. They don't consistently follow user intent
3. They can be verbose and unhelpful
4. "The language models we train can be made to behave in ways that are not aligned with user intent"

The goal: train language models to be helpful, honest, and harmless by using human feedback to fine-tune them.

## Key Idea / Architecture

InstructGPT uses a three-stage approach to align language models with human preferences:

### Stage 1: Supervised Fine-Tuning (SFT)

Collect human-written demonstrations of desired behavior:
- Human labelers write answers to various prompts
- Fine-tune GPT-3 on these demonstrations
- Creates a supervised baseline model

### Stage 2: Reward Model Training

Train a reward model to predict human preferences:
- Collect pairs of model outputs for the same prompt
- Human labelers rank which output is better
- Train a reward model to predict these rankings
- Reward model is initialized from GPT-3

### Stage 3: Reinforcement Learning from Human Feedback (RLHF)

Use PPO (Proximal Policy Optimization) to optimize the language model:
- Generate outputs from the current policy
- Score outputs with the reward model
- Optimize policy to maximize reward while staying close to SFT model
- Use KL divergence penalty to prevent reward hacking

### The RLHF Objective

$$\max_{\pi_\theta} \mathbb{E}_{x \sim D, y \sim \pi_\theta(y|x)} [r_\phi(x, y)] - \beta \cdot D_{KL}[\pi_\theta(y|x) || \pi_{ref}(y|x)]$$

where:
- $r_\phi$ is the reward model
- $\pi_\theta$ is the policy being trained
- $\pi_{ref}$ is the reference (SFT) policy
- $\beta$ controls the KL penalty strength

## Key Contributions

1. **Three-stage RLHF pipeline** - SFT → Reward Model → PPO is now standard
2. **Demonstrated alignment with human preferences** - 1.3B InstructGPT preferred to 175B GPT-3
3. **Showed generalization** - Model generalizes to tasks not seen in fine-tuning
4. **Improved safety** - 25% reduction in harmful outputs vs GPT-3

## Results

- **Human preference:** InstructGPT-1.3B preferred to GPT-3-175B 85% of the time
- **TruthfulQA:** 78% vs 27% for GPT-3 (much more honest)
- **Safety:** 25% reduction in harmful outputs on real-user prompts
- **SFT generalization:** Model improves on held-out task types not seen during fine-tuning
- **Win rates:** 85% preference over GPT-3 on API prompts, 71% on research prompts

### Key Observations

1. **Small models with alignment can beat large unaligned models** - InstructGPT-1.3B > GPT-3-175B
2. **Labeler agreement is high** - ~72% agreement on output rankings
3. **Alignment doesn't hurt performance** - InstructGPT still performs well on standard benchmarks
4. **Mode collapse is minimal** - Model doesn't become degenerate

## Why It Matters

InstructGPT established the paradigm for making language models safe and useful:

1. **RLHF becomes standard** - ChatGPT, Claude, and other assistants use this approach
2. **Alignment is achievable** - Human feedback can effectively shape model behavior
3. **Small aligned models > large unaligned models** - Quality of training matters more than scale
4. **Foundation for ChatGPT** - Directly led to the GPT-3.5 and ChatGPT models

## Weaknesses

- **Labeler biases** - Human preferences reflect labeler demographics and biases
- **Reward hacking** - Model may find ways to maximize reward without actually being better
- **Limited to text classification** - Reward model may not capture all aspects of quality
- **Expensive to train** - Requires collecting large amounts of human feedback
- **Scalability concerns** - How to align models as they become even larger

## Follow-up Work

- **ChatGPT:** Built on GPT-3.5 with RLHF
- **Constitutional AI:** Self-improvement using AI feedback
- **DPO:** Direct Preference Optimization without explicit reward model
- **RLHF alternatives:** KTO, IPO, and other alignment techniques