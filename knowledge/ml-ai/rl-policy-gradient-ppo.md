---
topic: ml-ai
difficulty: hard
tags: [rl, policy-gradient, ppo, rlhf]
---

# RL Policy Gradient, PPO & RLHF

## Policy Gradient Methods

Directly parameterize policy π_θ(a|s) — no need for value function (though one helps).

### Policy Gradient Theorem
```
∇_θ J(θ) = E_π[∇_θ log π_θ(a|s) · Q^π(s, a)]
```
- High-probability actions with high Q-value: increase probability
- High-probability actions with low Q-value: decrease probability

### REINFORCE (Monte Carlo Policy Gradient)
- Use actual return G_t as estimate of Q^π(s, a):
```
θ ← θ + α ∇_θ log π_θ(a_t|s_t) · G_t
```
- **High variance** due to Monte Carlo returns

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

## Actor-Critic Methods

**Actor** (policy π_θ): decides what to do.
**Critic** (value function V_φ): evaluates the actor's action.

### A2C / A3C
- A3C: Asynchronous parallel workers updating a global model
- A2C: Synchronous version — often faster due to better GPU utilization

### PPO (Proximal Policy Optimization)
Most widely used policy gradient algorithm (used in RLHF, robotics).

**PPO-Clip Objective**:
```
L(θ) = E[min(r_t(θ) A_t, clip(r_t(θ), 1-ε, 1+ε) A_t)]
```
Where r_t(θ) = π_θ(a|s) / π_{θ_old}(a|s) is the probability ratio.

- Prevents destructively large policy updates
- ε ∈ [0.1, 0.2] typically
- Stable, sample-efficient, simple to implement

## Maximum Entropy RL: SAC

**Soft Actor-Critic (SAC)**: Maximize both expected return AND policy entropy:
```
J(π) = E_π[Σ_t γ^t (R_t + α H(π(·|s_t)))]
```
- **Entropy bonus** encourages exploration and produces robust, multimodal policies
- Off-policy: uses replay buffer — sample efficient
- Popular in continuous control / robotics

## RL for LLMs (RLHF)

### Three-Phase LLM Pipeline
1. **Pre-training**: Self-supervised next-token prediction on web-scale data → knowledgeable but unaligned base model
2. **Supervised Fine-Tuning (SFT)**: Train on human prompt-response pairs → learns instruction following
3. **RLHF**: Reward model scores LLM outputs; PPO maximizes reward → alignment, safety, reduced hallucination

### Domain-Specific: Code Models
- **Fill-In-The-Middle (FIM)**: Predict missing code blocks from surrounding context
- **RLAIF/RLEF**: Reward from execution environment (compiler/linter) — positive reward for passing tests

## Algorithm Selection

| Algorithm | Type | On/Off-Policy | Best For |
|---|---|---|---|
| Q-Learning | Value | Off-policy | Simple discrete problems |
| DQN | Value (deep) | Off-policy | Atari, games |
| PPO | Actor-Critic | On-policy | General purpose, RLHF |
| SAC | Actor-Critic | Off-policy | Robotics, continuous control |
