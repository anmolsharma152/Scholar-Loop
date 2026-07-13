---
topic: papers
difficulty: hard
tags: [paper, dqn, reinforcement-learning, deep-learning, atari]
---

# Playing Atari with Deep Reinforcement Learning

**Authors:** Mnih et al. (DeepMind)
**Published:** 2013 (NIPS Deep Learning Workshop)
**arXiv:** 1312.5602

## Problem & Motivation

Reinforcement learning has been successful in many domains, but:
1. **Feature engineering** - Tabular methods require hand-crafted features
2. **Generalization** - Hard to generalize across similar states
3. **High-dimensional inputs** - Raw pixels are too high-dimensional for tabular methods

The goal: combine deep learning with reinforcement learning to learn directly from raw pixels.

## Key Idea / Architecture

### Deep Q-Network (DQN)

**Core Idea:** Use a deep neural network to approximate the Q-function $Q(s, a)$.

**Architecture:**
- Input: 84x84x4 (grayscale, stacked frames)
- Conv1: 8x8, stride 4, 32 filters
- Conv2: 4x4, stride 2, 64 filters
- Conv3: 3x3, stride 1, 64 filters
- FC: 512 units
- Output: Q-values for each action (18 Atari actions)

### Key Innovations

1. **Experience Replay:**
   - Store transitions (s, a, r, s') in replay memory
   - Sample random mini-batches for training
   - Breaks temporal correlations in experience

2. **Target Network:**
   - Use a separate target network (updated periodically)
   - Stabilizes training by fixing targets

3. **Epsilon-Greedy Exploration:**
   - With probability ε, take random action
   - Otherwise, take best action according to Q-values
   - ε annealed from 1.0 to 0.1 over training

### Training Algorithm

```
Initialize replay memory D
Initialize action-value network Q with random weights θ
Initialize target network Q̂ with weights θ⁻ = θ

For each episode:
  For each step:
    1. With probability ε, select random action a
       Otherwise select a = argmax_a Q(s, a; θ)
    2. Execute action a, observe reward r and new state s'
    3. Store (s, a, r, s') in D
    4. Sample random mini-batch from D
    5. Compute targets:
       y = r if episode ends
       y = r + γ max_a' Q̂(s', a'; θ⁻) otherwise
    6. Update θ to minimize (y - Q(s, a; θ))²
    7. Every C steps, update Q̂ ← Q
```

## Key Contributions

1. **First successful deep RL agent** - Learned to play Atari from pixels
2. **End-to-end learning** - No feature engineering needed
3. **Experience replay** - Stabilizes training with neural networks
4. **Target networks** - Further stabilizes Q-learning
5. **General architecture** - Same algorithm works across many games

## Results

- **49 out of 57 Atari games** - DQN achieves human-level performance
- **Games with superhuman performance:** Breakout, Pong, Space Invaders, Seaquest
- **Score:** Averaged 75% of human performance across all games
- **Training:** 200M frames (~500 hours of gameplay)

### Notable Game Performance

| Game | DQN | Human | Random |
|------|-----|-------|--------|
| Breakout | 401.3 | 31.8 | 1.3 |
| Pong | 20.9 | 9.3 | -20.7 |
| Space Invaders | 1976 | 1652 | 148 |
| Seaquest | 5284 | 11201 | 290 |

## Why It Matters

DQN launched the deep reinforcement learning revolution:

1. **Proof of concept** - Showed deep learning can work with RL
2. **General agent** - Same architecture across many games
3. **NeurIPS 2015 paper** - Influential follow-up paper
4. **Foundation for improvements** - Led to Double DQN, Dueling DQN, Rainbow

## Weaknesses

- **Sample inefficiency** - Requires 200M frames to train
- **Overestimation bias** - Q-values tend to be overestimated
- **Limited to discrete actions** - Can't handle continuous action spaces
- **Game-specific** - Different hyperparameters needed for different games
- **No exploration bonus** - Pure epsilon-greedy exploration is limited

## Follow-up Work

- **Double DQN:** Reduces overestimation bias
- **Dueling DQN:** Separate value and advantage streams
- **Prioritized Experience Replay:** Sample important transitions more often
- **Rainbow:** Combines multiple improvements
- **A3C/PPO:** Actor-critic methods that became more popular