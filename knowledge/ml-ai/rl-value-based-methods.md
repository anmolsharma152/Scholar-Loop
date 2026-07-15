---
topic: ml-ai
difficulty: hard
tags: [rl, value-based, dqn]
---

# RL Value-Based Methods: Q-Learning & DQN

## Model-Free RL

Agent does NOT know P or R — must learn from interaction.

### Monte Carlo Methods
- Learn from **complete episodes** (wait until termination)
- Update V(s) or Q(s,a) with the actual return G_t observed
- **Pros**: Unbiased (uses actual returns)
- **Cons**: High variance; can only apply to episodic tasks

### Temporal Difference (TD) Learning
- Learns from **incomplete episodes** — updates after each step
- **TD(0) update**: `V(S_t) ← V(S_t) + α [R_{t+1} + γ V(S_{t+1}) - V(S_t)]`
- The term `R_{t+1} + γ V(S_{t+1})` is the **TD target**; the difference is the **TD error**

## Q-Learning (Off-Policy TD Control)

```
Q(S_t, A_t) ← Q(S_t, A_t) + α [R_{t+1} + γ max_a Q(S_{t+1}, a) - Q(S_t, A_t)]
```

- **Off-policy**: Learns Q* while following a behavioral policy (e.g., ε-greedy)
- Converges to optimal Q* given sufficient exploration and learning rate decay

### SARSA (On-Policy TD Control)
```
Q(S_t, A_t) ← Q(S_t, A_t) + α [R_{t+1} + γ Q(S_{t+1}, A_{t+1}) - Q(S_t, A_t)]
```

- **On-policy**: Updates based on the action actually taken
- More conservative than Q-Learning — learns Q^π for the current policy

### Exploration vs. Exploitation
- **ε-greedy**: With probability ε, explore (random action); with probability 1-ε, exploit (greedy action)
- **Decay ε** over time: high exploration early, exploitation later
- **Boltzmann exploration**: Sample actions proportional to Q-values (softmax)

## Deep Q-Networks (DQN)

Tabular Q-learning fails in large/continuous state spaces — use neural network as function approximator.

### Core DQN (DeepMind, 2015)
- Q-network: Q(s, a; θ) approximates Q*(s, a)
- **Experience Replay**: Store transitions (s, a, r, s') in replay buffer; sample random mini-batches to break temporal correlation
- **Target Network**: Separate network Q(s, a; θ⁻) with frozen parameters updated periodically — stabilizes training
- Loss: L(θ) = E[(r + γ max_a' Q(s', a'; θ⁻) - Q(s, a; θ))²]

### Double DQN
- Problem: Standard DQN overestimates Q-values (max operator bias)
- Fix: Use **online network** to select best action, **target network** to evaluate it:
```
y = r + γ Q(s', argmax_{a'} Q(s', a'; θ); θ⁻)
```

### Dueling DQN
- Split Q-value into **state value V(s)** and **advantage A(s, a)**:
```
Q(s, a) = V(s) + A(s, a) - mean_a' A(s, a')
```
- Learns which states are valuable regardless of action — better generalization

### Prioritized Experience Replay
- Sample transitions with probability proportional to TD error |δ| (high-error transitions are more informative)
- Uses importance sampling weights to correct bias from non-uniform sampling
