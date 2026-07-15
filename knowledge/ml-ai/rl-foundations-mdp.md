---
topic: ml-ai
difficulty: hard
tags: [rl, mdp, foundations]
---

# RL Foundations: MDP & Bellman Equations

## Markov Decision Process (MDP)

An MDP is defined by ⟨S, A, P, R, γ⟩:

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

## Return and Value Functions

- **Return**: G_t = Σ_{k=0}^{∞} γ^k R_{t+k+1} (discounted cumulative future reward)
- **State-Value Function V^π(s)**: Expected return from state s following policy π
- **Action-Value Function Q^π(s, a)**: Expected return from state s taking action a, then following π

## Bellman Equations

**Bellman Expectation Equation**:
```
V^π(s) = Σ_a π(a|s) Σ_{s'} P(s'|s,a) [R(s,a,s') + γ V^π(s')]
```

**Bellman Optimality Equation**:
```
V*(s) = max_a Σ_{s'} P(s'|s,a) [R(s,a,s') + γ V*(s')]
Q*(s,a) = Σ_{s'} P(s'|s,a) [R(s,a,s') + γ max_{a'} Q*(s',a')]
```

## Planning (Model-Based) Methods

When P and R are known, solve MDP via dynamic programming.

### Policy Iteration
```
1. Initialize arbitrary policy π₀
2. Repeat:
   a. Policy Evaluation: compute V^{π_k}(s) for all s
   b. Policy Improvement: π_{k+1}(s) = argmax_a Q^{π_k}(s, a)
3. Until π_{k+1} = π_k (optimal policy found)
```

### Value Iteration
Combines evaluation and improvement in one sweep:
```
V_{k+1}(s) = max_a Σ_{s'} P(s'|s,a) [R(s,a,s') + γ V_k(s')]
```

After convergence, extract optimal policy: π*(s) = argmax_a Q*(s, a).
