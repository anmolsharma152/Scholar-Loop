---
topic: ml-ai
difficulty: hard
tags: [rl, comprehensive]
---

# Reinforcement Learning: Comprehensive Guide

## 1. Foundations

### Markov Decision Process (MDP)
Defined by 5-tuple ⟨S, A, P, R, γ⟩:

| Symbol | Meaning |
|---|---|
| S | State space — all possible environment states |
| A | Action space — all valid agent actions |
| P | Transition matrix — P(s'|s, a) |
| R | Reward function — R(s, a) |
| γ | Discount factor ∈ [0, 1) — value of future vs. immediate rewards |

**Markov Property**: Future depends only on present, not past:
```
P[S_{t+1}=s', R_{t+1}=r | S_t, A_t, ..., S_0, A_0] = P[S_{t+1}=s', R_{t+1}=r | S_t, A_t]
```

### Return and Value Functions
- **Return**: G_t = Σ_{k=0}^{∞} γ^k R_{t+k+1} (discounted cumulative future reward)
- **State-Value Function V^π(s)**: Expected return from state s following policy π
- **Action-Value Function Q^π(s, a)**: Expected return from state s taking action a, then following π

### Bellman Equations
**Bellman Expectation Equation**:
```
V^π(s) = Σ_a π(a|s) Σ_{s'} P(s'|s,a) [R(s,a,s') + γ V^π(s')]
```

**Bellman Optimality Equation**:
```
V*(s) = max_a Σ_{s'} P(s'|s,a) [R(s,a,s') + γ V*(s')]
Q*(s,a) = Σ_{s'} P(s'|s,a) [R(s,a,s') + γ max_{a'} Q*(s',a')]
```

---

## 2. Planning (Model-Based) Methods

When P and R are known, solve MDP via dynamic programming.

### Policy Evaluation
Iteratively update V(s) toward V^π using Bellman expectation equation until convergence.

### Policy Iteration
```
1. Initialize arbitrary policy π₀
2. Repeat:
   a. Policy Evaluation: compute V^{π_k}(s) for all s
   b. Policy Improvement: π_{k+1}(s) = argmax_a Q^{π_k}(s, a)
3. Until π_{k+1} = π_k (optimal policy found)
```
Converges in a finite number of iterations (policy space is finite).

### Value Iteration
Combines evaluation and improvement in one sweep:
```
V_{k+1}(s) = max_a Σ_{s'} P(s'|s,a) [R(s,a,s') + γ V_k(s')]
```
After convergence, extract optimal policy: π*(s) = argmax_a Q*(s, a).

---

## 3. Model-Free RL

Agent does NOT know P or R — must learn from interaction.

### Monte Carlo Methods
- Learn from **complete episodes** (wait until termination).
- Update V(s) or Q(s,a) with the actual return G_t observed.
- **First-visit MC**: Update only on first visit to s in episode.
- **Every-visit MC**: Update on every visit.
- **Pros**: Unbiased (uses actual returns).
- **Cons**: High variance; can only apply to episodic tasks.

### Temporal Difference (TD) Learning
- Learns from **incomplete episodes** — updates after each step.
- **TD(0) update**:
```
V(S_t) ← V(S_t) + α [R_{t+1} + γ V(S_{t+1}) - V(S_t)]
```
The term `R_{t+1} + γ V(S_{t+1})` is the **TD target**; the difference is the **TD error**.
- **TD(λ)**: n-step returns and eligibility traces blend MC and TD.

---

## 4. Value-Based Methods

### Q-Learning (Off-Policy TD Control)
```
Q(S_t, A_t) ← Q(S_t, A_t) + α [R_{t+1} + γ max_a Q(S_{t+1}, a) - Q(S_t, A_t)]
```
- **Off-policy**: Learns Q* while following a behavioral policy (e.g., ε-greedy).
- Converges to optimal Q* given sufficient exploration and learning rate decay.

### SARSA (On-Policy TD Control)
```
Q(S_t, A_t) ← Q(S_t, A_t) + α [R_{t+1} + γ Q(S_{t+1}, A_{t+1}) - Q(S_t, A_t)]
```
- **On-policy**: Updates based on the action actually taken (A_{t+1} from current policy).
- More conservative than Q-Learning — learns Q^π for the current policy.

### Exploration vs. Exploitation
- **ε-greedy**: With probability ε, explore (random action); with probability 1-ε, exploit (greedy action).
- **Decay ε** over time: high exploration early, exploitation later.
- **Boltzmann exploration**: Sample actions proportional to Q-values (softmax).

---

## 5. Deep Q-Networks (DQN)

Tabular Q-learning fails in large/continuous state spaces — use neural network as function approximator.

### Core DQN (DeepMind, 2015)
- Q-network: Q(s, a; θ) approximates Q*(s, a).
- **Experience Replay**: Store transitions (s, a, r, s') in replay buffer; sample random mini-batches to break temporal correlation.
- **Target Network**: Separate network Q(s, a; θ⁻) with frozen parameters updated periodically — stabilizes training.
- Loss: L(θ) = E[(r + γ max_a' Q(s', a'; θ⁻) - Q(s, a; θ))²]

### Double DQN
- Problem: Standard DQN overestimates Q-values (max operator bias).
- Fix: Use **online network** to select best action, **target network** to evaluate it:
```
y = r + γ Q(s', argmax_{a'} Q(s', a'; θ); θ⁻)
```

### Dueling DQN
- Split Q-value into **state value V(s)** and **advantage A(s, a)**:
```
Q(s, a) = V(s) + A(s, a) - mean_a' A(s, a')
```
- Learns which states are valuable regardless of action — better generalization.

### Prioritized Experience Replay
- Sample transitions with probability proportional to TD error |δ| (high-error transitions are more informative).
- Uses importance sampling weights to correct bias from non-uniform sampling.

---

## 6. Policy Gradient Methods

Directly parameterize policy π_θ(a|s) — no need for value function (though one helps).

### Policy Gradient Theorem
```
∇_θ J(θ) = E_π[∇_θ log π_θ(a|s) · Q^π(s, a)]
```
- High-probability actions with high Q-value: increase probability.
- High-probability actions with low Q-value: decrease probability.

### REINFORCE (Monte Carlo Policy Gradient)
- Use actual return G_t as estimate of Q^π(s, a):
```
θ ← θ + α ∇_θ log π_θ(a_t|s_t) · G_t
```
- **High variance** due to Monte Carlo returns.

### Variance Reduction: Baselines
Subtract a baseline b(s) (e.g., V(s)) from Q:
```
θ ← θ + α ∇_θ log π_θ(a|s) · [Q(s,a) - b(s)]
```
Does not introduce bias; reduces variance significantly.

### Advantage Function
```
A(s, a) = Q(s, a) - V(s)
```
Estimated via **Generalized Advantage Estimation (GAE)**:
```
A_t = Σ_{l=0}^{∞} (γλ)^l δ_{t+l},   δ_t = r_t + γ V(s_{t+1}) - V(s_t)
```
λ ∈ [0,1] controls bias-variance tradeoff.

---

## 7. Actor-Critic Methods

**Actor** (policy π_θ): decides what to do.
**Critic** (value function V_φ): evaluates the actor's action.

### A2C / A3C
- Actor-critic with advantage estimates.
- A3C: Asynchronous parallel workers updating a global model.
- A2C: Synchronous version — often faster due to better GPU utilization.

### PPO (Proximal Policy Optimization)
Most widely used policy gradient algorithm (used in RLHF, robotics).

**PPO-Clip Objective**:
```
L(θ) = E[min(r_t(θ) A_t, clip(r_t(θ), 1-ε, 1+ε) A_t)]
```
Where r_t(θ) = π_θ(a|s) / π_{θ_old}(a|s) is the probability ratio.

- Prevents destructively large policy updates.
- ε ∈ [0.1, 0.2] typically.
- Stable, sample-efficient, simple to implement.

---

## 8. Maximum Entropy RL: SAC

**Soft Actor-Critic (SAC)**: Maximize both expected return AND policy entropy:
```
J(π) = E_π[Σ_t γ^t (R_t + α H(π(·|s_t)))]
```
- **Entropy bonus** encourages exploration and produces robust, multimodal policies.
- Off-policy: uses replay buffer — sample efficient.
- Automatic entropy temperature tuning.
- Popular in continuous control / robotics.

---

## 9. Algorithm Selection Guide

| Algorithm | Type | On/Off-Policy | Space | Best For |
|---|---|---|---|---|
| Value Iteration | Planning | N/A (model-based) | Discrete S,A | Known MDPs |
| Q-Learning | Value | Off-policy | Discrete A | Simple discrete problems |
| SARSA | Value | On-policy | Discrete A | Safe exploration |
| DQN | Value (deep) | Off-policy | Discrete A | Atari, games |
| Double DQN | Value (deep) | Off-policy | Discrete A | Reduces overestimation |
| Dueling DQN | Value (deep) | Off-policy | Discrete A | States more valuable than actions |
| REINFORCE | Policy | On-policy | Continuous A | Simple policy search |
| PPO | Actor-Critic | On-policy | Both | General purpose, RLHF, robotics |
| SAC | Actor-Critic | Off-policy | Continuous A | Robotics, continuous control |

---

## 10. RL for LLMs (RLHF)

### Three-Phase LLM Pipeline
1. **Pre-training**: Self-supervised next-token prediction on web-scale data → knowledgeable but unaligned base model.
2. **Supervised Fine-Tuning (SFT)**: Train on human prompt-response pairs → learns instruction following.
3. **RLHF**: Reward model scores LLM outputs; PPO maximizes reward → alignment, safety, reduced hallucination.

### Domain-Specific: Code Models
- **Fill-In-The-Middle (FIM)**: Predict missing code blocks from surrounding context.
- **RLAIF/RLEF**: Reward from execution environment (compiler/linter) — positive reward for passing tests, penalty for syntax errors.

---

## 11. Key Formulas Summary

```
Bellman Optimality:  V*(s) = max_a Σ_{s'} P(s'|s,a)[R + γV*(s')]
Q-Learning:         Q(s,a) ← Q(s,a) + α[r + γ max_{a'} Q(s',a') - Q(s,a)]
Policy Gradient:    ∇_θ J = E[∇_θ log π_θ(a|s) · A(s,a)]
PPO Clip:           L = min(r_t A_t, clip(r_t, 1±ε) A_t)
GAE Advantage:      A_t = Σ_l (γλ)^l δ_{t+l}
DQN Loss:           L = E[(r + γ max_{a'} Q(s',a';θ⁻) - Q(s,a;θ))²]
```
