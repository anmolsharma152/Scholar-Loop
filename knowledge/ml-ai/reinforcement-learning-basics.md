---
difficulty: medium
last_sent:
review_count: 0
tags:
  - rl
  - fundamentals
topic: ml-ai
---

# Reinforcement Learning Fundamentals

Reinforcement learning (RL) is a paradigm where an agent learns to make sequential decisions by interacting with an environment, receiving rewards or penalties, and optimizing a policy to maximize cumulative return. Unlike supervised learning, the agent discovers optimal behavior through trial and error rather than labeled examples.

## Core Components

An RL system consists of an **agent** (the learner/decision-maker) and an **environment** (everything the agent interacts with). At each timestep, the agent observes a **state** $s$, takes an **action** $a$, receives a **reward** $r$, and transitions to a new state $s'$.

| Component | Description | Example (Chess) |
|-----------|-------------|-----------------|
| Agent | The learner | Chess engine |
| Environment | The world | Chess board + rules |
| State | Current situation | Board configuration |
| Action | Possible moves | Legal moves available |
| Reward | Feedback signal | +1 win, -1 loss, 0 draw |
| Policy | Strategy | Mapping from board → move |
| Value Function | Expected return | How good is a board position |

## Markov Decision Processes (MDPs)

Formally, RL problems are modeled as MDPs defined by the tuple $(S, A, P, R, \gamma)$:

- **S**: Set of states
- **A**: Set of actions
- **P**: Transition probability $P(s'|s,a)$
- **R**: Reward function $R(s,a,s')$
- **Discount factor** $\gamma \in [0,1]$: Controls how much future rewards matter

The Markov property states that the future depends only on the present, not the history.

## Policy, Value Function, and Q-Function

A **policy** $\pi(a|s)$ is the agent's strategy — a mapping from states to actions (or action probabilities).

The **state-value function** $V^\pi(s)$ is the expected cumulative reward starting from state $s$ and following policy $\pi$:

$$V^\pi(s) = \mathbb{E}\left[\sum_{t=0}^{\infty} \gamma^t r_t \mid s_0 = s, \pi\right]$$

The **action-value function** (Q-function) $Q^\pi(s,a)$ is the expected cumulative reward from taking action $a$ in state $s$ and then following $\pi$:

$$Q^\pi(s,a) = \mathbb{E}\left[\sum_{t=0}^{\infty} \gamma^t r_t \mid s_0 = s, a_0 = a, \pi\right]$$

## Bellman Equations

The Bellman equation decomposes the value function recursively:

$$V^\pi(s) = \sum_a \pi(a|s) \sum_{s'} P(s'|s,a) \left[R(s,a,s') + \gamma V^\pi(s')\right]$$

The optimal policy satisfies the **Bellman optimality equation**:

$$Q^*(s,a) = R(s,a) + \gamma \sum_{s'} P(s'|s,a) \max_{a'} Q^*(s',a')$$

## Exploration vs Exploitation

A fundamental tension in RL:

- **Exploitation**: Choose the best-known action to maximize immediate reward
- **Exploration**: Try uncertain actions to discover potentially better strategies

Common strategies include $\varepsilon$-greedy (act randomly with probability $\varepsilon$), Upper Confidence Bound (UCB), and Thompson Sampling. The optimal balance depends on the problem — in stationary environments, exploration can decrease over time.

## Monte Carlo vs Temporal Difference Learning

```python
# Monte Carlo: update after full episode
# V(s) ← V(s) + α [G_t - V(s)]
# where G_t = actual return from episode

# Temporal Difference: update after each step
# V(s) ← V(s) + α [r + γV(s') - V(s)]
# TD uses bootstrap estimate (r + γV(s')) instead of actual return
```

TD learning (e.g., Q-learning, SARSA) is more common because it doesn't require waiting for episode completion and can learn from incomplete episodes.

## Q-Learning (Tabular)

```python
import numpy as np

# Initialize Q-table
Q = np.zeros((n_states, n_actions))

# Q-learning update
def q_learning(state, action, reward, next_state, alpha=0.1, gamma=0.99):
    best_next = np.max(Q[next_state])
    td_target = reward + gamma * best_next
    td_error = td_target - Q[state, action]
    Q[state, action] += alpha * td_error
```

Key properties: Q-learning is **off-policy** (learns about greedy policy while following exploratory policy) and **model-free** (no need for transition model $P$).

## Key Takeaways

- RL differs from supervised/unsupervised learning through its interactive, reward-driven nature
- MDPs provide the formal framework; the goal is finding the optimal policy $\pi^*$
- Exploration vs exploitation is a core challenge that affects all RL algorithms
- Tabular methods work for small, discrete state spaces but don't scale — deep RL (DQN, PPO) is needed for complex problems
- The discount factor $\gamma$ trades off short-term vs long-term reward

## Common Bugs

| Bug | Symptom | Fix |
|-----|---------|-----|
| Forgetting to discount rewards | Training instability | Apply $\gamma^t$ to returns |
| No exploration | Suboptimal convergence | Use $\varepsilon$-greedy with decay |
| Reward shaping that creates loops | Agent exploits reward hack | Design sparse or well-shaped rewards |
| Wrong TD target computation | Diverging Q-values | Ensure bootstrap is `r + γ max Q(s',a')` |
| Using on-policy data in off-policy algo | Inconsistent updates | Use experience replay buffer |
