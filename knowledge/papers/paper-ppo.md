---
topic: papers
difficulty: hard
tags: [paper, ppo, reinforcement-learning, policy-optimization, policy-gradient]
---

# Proximal Policy Optimization Algorithms

**Authors:** Schulman, Wolski, Dhariwal, Radford, Klimov (OpenAI)
**Published:** 2017
**arXiv:** 1707.06347

## Problem & Motivation

Policy gradient methods for reinforcement learning suffer from:
1. **Sample inefficiency** - Require many samples to make stable updates
2. **Training instability** - Large policy updates can cause performance collapse
3. **Sensitivity to hyperparameters** - Tuning learning rates and step sizes is difficult
4. **Trust region methods are complex** - TRPO uses natural gradients which are computationally expensive

The goal: develop a policy optimization method that is simple, scalable, and stable.

## Key Idea / Architecture

### Trust Region Policy Optimization (TRPO) Background

TRPO constrains policy updates to a trust region:
$$\max_\theta \mathbb{E}[A_t(\theta)] \text{ subject to } D_{KL}[\pi_{\theta_{old}} || \pi_\theta] \leq \delta$$

This is effective but requires complex second-order optimization (conjugate gradient).

### Proximal Policy Optimization (PPO)

PPO uses a simpler surrogate objective with clipping:

$$L^{CLIP}(\theta) = \mathbb{E}_t \left[ \min \left( r_t(\theta) A_t, \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon) A_t \right) \right]$$

where $r_t(\theta) = \frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_{old}}(a_t|s_t)}$ is the probability ratio.

### PPO-Clip vs PPO-Penalty

- **PPO-Clip:** Clip the probability ratio (most commonly used)
- **PPO-Penalty:** Add KL penalty to objective (similar to TRPO but simpler)

### Why Clipping Works

- When $A_t > 0$ (good action): maximization pushes $r_t$ up, but clipping limits how much
- When $A_t < 0$ (bad action): minimization pushes $r_t$ down, but clipping limits how much
- Prevents destructive large policy updates

### Actor-Critic Architecture

- **Actor (Policy):** Neural network that outputs action probabilities
- **Critic (Value function):** Neural network that estimates state value V(s)
- **GAE (Generalized Advantage Estimation):** Combines multiple advantage estimates

## Key Contributions

1. **Simple clipping mechanism** - Effective and easy to implement
2. **Sample efficiency** - Better than vanilla policy gradients
3. **Scalability** - Works well with large neural networks
4. **Wide applicability** - Effective across many domains (games, robotics, RLHF)

## Results

- **Atari games:** Matches or exceeds TRPO performance
- **MuJoCo locomotion:** Competitive with other policy gradient methods
- **Robotics:** Successfully trains robotic manipulation policies
- **RLHF:** Standard algorithm for aligning language models with human feedback

### Comparison to Other Methods

| Method | Stability | Sample Efficiency | Implementation |
|--------|-----------|-------------------|----------------|
| REINFORCE | Low | Low | Simple |
| A2C | Medium | Medium | Simple |
| TRPO | High | Medium-High | Complex |
| PPO | High | High | Simple |

## Why It Matters

PPO became the de facto standard for many RL applications:

1. **RLHF backbone** - Used to train InstructGPT, ChatGPT, Claude
2. **Game AI** - Trained OpenAI Five, Dota 2 bots
3. **Robotics** - Used for sim-to-real transfer
4. **Simple and reliable** - Easy to implement and tune

## Weaknesses

- **Clipping sensitivity** - Clip ratio ε needs tuning
- **On-policy only** - Can't reuse old data efficiently
- **Computational cost** - Requires multiple epochs per batch
- **Not optimal for all tasks** - Some tasks may benefit from off-policy methods

## Follow-up Work

- **PPO for RLHF:** Application to language model alignment
- **RLOO:** Reduced variance variant
- **ReMax:** Variance reduction techniques
- **DPO:** Alternative to RLHF that doesn't need PPO