---
difficulty: hard
last_sent:
review_count: 0
tags:
  - rl
  - dqn
  - ppo
  - deep-rl
topic: ml-ai
---

# Deep Reinforcement Learning: DQN, Policy Gradient, and PPO

Deep RL replaces tabular value functions and policies with neural networks, enabling RL to scale to high-dimensional state spaces like images and sensor data. This note covers the foundational algorithms: DQN, REINFORCE, Actor-Critic, and PPO.

## Why Deep RL?

Tabular methods fail when state spaces are large or continuous (e.g., pixels in an Atari game = $256^{210 \times 160 \times 3}$ possible states). Neural networks serve as function approximators for $Q(s,a)$ or $\pi(a|s)$.

| Approach | Learns | Type | Limitations |
|----------|--------|------|-------------|
| Tabular Q-learning | Q-table | Value-based | Doesn't scale |
| DQN | Q-network | Value-based | Discrete actions only |
| REINFORCE | Policy network | Policy-based | High variance |
| Actor-Critic | Both networks | Hybrid | More complex |
| PPO | Both networks | Hybrid | Current standard |

## Deep Q-Network (DQN)

DQN (Mnih et al., 2015) uses two key innovations to stabilize training:

1. **Experience replay**: Store transitions $(s, a, r, s')$ in a buffer and sample random mini-batches, breaking temporal correlations in sequential data
2. **Target network**: A periodically-updated copy of the Q-network used to compute TD targets, preventing the "moving target" problem

```python
import torch
import torch.nn as nn
import random
from collections import deque

class DQN(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, 128), nn.ReLU(),
            nn.Linear(128, 128), nn.ReLU(),
            nn.Linear(128, action_dim)
        )
    
    def forward(self, x):
        return self.net(x)

class ReplayBuffer:
    def __init__(self, capacity=100000):
        self.buffer = deque(maxlen=capacity)
    
    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        return (torch.FloatTensor(states), torch.LongTensor(actions),
                torch.FloatTensor(rewards), torch.FloatTensor(next_states),
                torch.FloatTensor(dones))

def train_dqn(q_net, target_net, buffer, optimizer, batch_size=64, gamma=0.99):
    states, actions, rewards, next_states, dones = buffer.sample(batch_size)
    
    q_values = q_net(states).gather(1, actions.unsqueeze(1)).squeeze(1)
    with torch.no_grad():
        next_q = target_net(next_states).max(1)[0]
        target = rewards + gamma * next_q * (1 - dones)
    
    loss = nn.MSELoss()(q_values, target)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
```

**DQN Loss**: $\mathcal{L} = \mathbb{E}\left[\left(r + \gamma \max_{a'} Q_{\text{target}}(s', a') - Q(s, a)\right)^2\right]$

## Policy Gradient: REINFORCE

REINFORCE directly optimizes the policy $\pi_\theta(a|s)$ by estimating the gradient of expected return:

$$\nabla_\theta J(\theta) = \mathbb{E}_\pi\left[\sum_t \nabla_\theta \log \pi_\theta(a_t|s_t) \cdot G_t\right]$$

where $G_t = \sum_{k=t}^{T} \gamma^{k-t} r_k$ is the discounted return from step $t$.

```python
def reinforce_update(policy, states, actions, returns):
    log_probs = policy.log_prob(actions)
    loss = -(log_probs * returns).mean()
    loss.backward()
```

**Problem**: High variance in $G_t$ estimates leads to unstable training. This motivates **Actor-Critic** methods.

## Actor-Critic

Combines a **policy network** (actor) that selects actions and a **value network** (critic) that estimates $V(s)$ to reduce variance:

- Actor: $\pi_\theta(a|s)$ — parametrized policy
- Critic: $V_w(s)$ — value function for variance reduction

The advantage function $A(s,a) = Q(s,a) - V(s)$ measures how much better action $a$ is compared to the average action. Using the critic's estimate, we can compute advantages without the full Q-function.

## Proximal Policy Optimization (PPO)

PPO (Schulman et al., 2017) is the dominant RL algorithm in practice (used in RLHF, robotics, game AI). It prevents destructive large policy updates via a **clipped surrogate objective**:

$$\mathcal{L}^{CLIP}(\theta) = \mathbb{E}\left[\min\left(r_t(\theta) A_t, \text{clip}(r_t(\theta), 1-\varepsilon, 1+\varepsilon) A_t\right)\right]$$

where $r_t(\theta) = \frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_{\text{old}}}(a_t|s_t)}$ is the probability ratio.

```python
import torch.nn.functional as F

def ppo_update(policy, value_net, optimizer, states, actions, old_log_probs,
               advantages, returns, clip_eps=0.2, epochs=4):
    for _ in range(epochs):
        new_log_probs = policy.log_prob(actions)
        ratio = torch.exp(new_log_probs - old_log_probs)
        
        surr1 = ratio * advantages
        surr2 = torch.clamp(ratio, 1 - clip_eps, 1 + clip_eps) * advantages
        policy_loss = -torch.min(surr1, surr2).mean()
        
        value_preds = value_net(states).squeeze()
        value_loss = F.mse_loss(value_preds, returns)
        
        loss = policy_loss + 0.5 * value_loss
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
```

## Algorithm Comparison

| Algorithm | Policy Type | On/Off-Policy | Variance | Stability | Sample Efficiency |
|-----------|-------------|---------------|----------|-----------|-------------------|
| DQN | Value-based | Off | Low | Medium | Medium |
| REINFORCE | Policy-based | On | High | Low | Low |
| A2C/A3C | Actor-Critic | On | Medium | Medium | Medium |
| PPO | Actor-Critic | On (clipped) | Medium | High | Medium-High |
| SAC | Actor-Critic | Off | Low | High | High |

## Key Takeaways

- DQN revolutionized RL by combining neural networks with experience replay and target networks
- Policy gradient methods directly optimize the policy but suffer from high variance
- Actor-Critic methods reduce variance by using a learned value baseline
- PPO's clipped objective is the practical default — stable, simple, and effective
- Deep RL requires careful hyperparameter tuning; small changes can cause divergence
- Sample efficiency remains a challenge — model-based RL and offline RL are active research areas

## Common Bugs

| Bug | Symptom | Fix |
|-----|---------|-----|
| Not syncing target network in DQN | Diverging Q-values | Hard/soft update target net periodically |
| Forgetting to detach target in TD | Graph explosion | Use `torch.no_grad()` for target computation |
| Wrong advantage computation | Policy goes in wrong direction | Normalize advantages (subtract mean, divide by std) |
| Clip ratio too small | Policy barely updates | Try $\varepsilon = 0.2$ (default) |
| Using REINFORCE without baseline | Unstable training | Subtract baseline $V(s)$ from returns |
| Not resetting gradients | Accumulated gradients | Always call `optimizer.zero_grad()` |
