---
topic: papers
difficulty: hard
tags: [paper, ddpg, deep-reinforcement-learning, continuous-control, actor-critic]
---

# Continuous Control with Deep Reinforcement Learning

**Authors:** Lillicrap et al. (DeepMind)
**Published:** ICLR 2016
**arXiv:** 1509.02971

## Problem & Motivation

Deep RL has been successful in discrete action spaces (Atari games), but:
1. **Discretization** - Converting continuous to discrete loses information
2. **Curse of dimensionality** - Tabular methods can't handle continuous spaces
3. **Exploration** - Random exploration doesn't work well in continuous spaces
4. **Stability** - Combining function approximation with RL is unstable

The goal: extend deep RL to continuous action spaces.

## Key Idea / Architecture

### Deep Deterministic Policy Gradient (DDPG)

**Actor-Critic architecture:**
- **Actor (policy):** Maps states to actions: $\mu(s|\theta^\mu)$
- **Critic (Q-function):** Estimates Q-value: $Q(s, a|\theta^Q)$

**Deterministic policy:**
- Actor outputs a single action (not distribution)
- Gradient of Q-value with respect to actions gives direction

### Key Innovations

1. **Experience Replay:**
   - Store transitions (s, a, r, s') in replay buffer
   - Sample random mini-batches for training
   - Breaks temporal correlations

2. **Target Networks:**
   - Separate target networks for actor and critic
   - Soft updates: $\theta' \leftarrow \tau \theta + (1-\tau) \theta'$
   - Stabilizes training

3. **Deterministic Policy Gradient:**
   $$\nabla_{\theta^\mu} J \approx \mathbb{E}[\nabla_a Q(s, a|\theta^Q)|_{a=\mu(s)} \nabla_{\theta^\mu} \mu(s|\theta^\mu)]$$

   Q-gradient with respect to actions guides actor updates.

### Training Algorithm

```
Initialize actor μ, critic Q with random weights
Initialize target networks μ', Q' with μ, Q weights
Initialize replay buffer R

For each episode:
  For each step:
    1. Select action: a = μ(s) + noise (exploration)
    2. Execute action, observe reward r and new state s'
    3. Store (s, a, r, s') in R
    4. Sample random mini-batch from R
    5. Update critic: minimize (y - Q(s, a))²
       where y = r + γ Q'(s', μ'(s'))
    6. Update actor: gradient ascent on Q(s, μ(s))
    7. Soft update target networks
```

### Exploration

Add noise to actions during exploration:
- **Ornstein-Uhlenbeck:** Temporally correlated noise
- **Gaussian noise:** Simple independent noise

## Key Contributions

1. **Continuous action spaces** - First successful deep RL for continuous control
2. **Deterministic policy gradient** - Simple and effective gradient computation
3. **Stable training** - Target networks and replay buffer enable stability
4. **End-to-end learning** - No hand-crafted features needed

## Results

- **MuJoCo tasks:** Competitive with state-of-the-art
- **Reacher:** 2.5 degree error (vs 3.0 for other methods)
- **Walker:** 1.5 score (competitive with policy gradient methods)
- **Ant:** 3.1 score (good locomotion)
- **Humanoid:** Competitive with model-based methods

### Comparison

| Method | Reacher | Walker | Ant |
|--------|---------|--------|-----|
| DDPG | 2.5 | 1.5 | 3.1 |
| TRPO | 2.8 | 1.7 | 3.5 |
| Policy Gradient | 3.0 | 1.8 | 3.8 |

## Why It Matters

DDPG enabled continuous control in deep RL:

1. **Robotics** - Sim-to-real transfer for robotic manipulation
2. **Control** - Autonomous systems, drones, vehicles
3. **Game AI** - Continuous actions in complex environments
4. **Foundation for TD3/SAC** - Led to improved algorithms

## Weaknesses

- **Overestimation bias** - Q-values tend to be overestimated
- **Exploration challenges** - Noise may not explore well in high dimensions
- **Hyperparameter sensitivity** - Requires careful tuning
- **Sample inefficiency** - Requires many environment interactions
- **No stochastic policies** - Can't handle exploration/exploitation trade-off optimally

## Follow-up Work

- **TD3:** Twin Delayed DDPG - addresses overestimation
- **SAC:** Soft Actor-Critic - entropy-regularized, stochastic
- **PPO for continuous:** Adapts PPO to continuous actions
- **Model-based methods:** Learn environment model for planning