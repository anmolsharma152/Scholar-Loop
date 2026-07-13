---
topic: papers
difficulty: hard
tags: [paper, adam, optimizer, deep-learning, optimization]
---

# Adam: A Method for Stochastic Optimization

**Authors:** Kingma & Ba (University of Amsterdam)
**Published:** ICLR 2015
**arXiv:** 1412.6980

## Problem & Motivation

Training deep neural networks requires efficient optimization algorithms. Existing methods have limitations:
1. **SGD** - Slow convergence, sensitive to learning rate
2. **Momentum** - Better but still requires careful tuning
3. **AdaGrad** - Good for sparse data but learning rate decays too quickly
4. **RMSProp** - Addresses AdaGrad's decay but lacks theoretical analysis

The goal: develop an optimizer that combines the advantages of momentum and adaptive learning rates.

## Key Idea / Architecture

### Adam (Adaptive Moment Estimation)

Maintains exponential moving averages of:
1. **First moment (mean):** $m_t = \beta_1 m_{t-1} + (1-\beta_1) g_t$
2. **Second moment (uncentered variance):** $v_t = \beta_2 v_{t-1} + (1-\beta_2) g_t^2$

**Bias correction:**
$$\hat{m}_t = \frac{m_t}{1 - \beta_1^t}, \quad \hat{v}_t = \frac{v_t}{1 - \beta_2^t}$$

**Parameter update:**
$$\theta_{t+1} = \theta_t - \eta \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon}$$

### Hyperparameters

- $\eta$ = learning rate (default: 0.001)
- $\beta_1$ = exponential decay rate for first moment (default: 0.9)
- $\beta_2$ = exponential decay rate for second moment (default: 0.999)
- $\epsilon$ = small constant for numerical stability (default: 1e-8)

### Key Properties

1. **Adaptive learning rates** - Each parameter gets its own learning rate
2. **Momentum** - Accelerates convergence in consistent gradient directions
3. **Bias correction** - Corrects for initialization bias in moments
4. **Computational efficiency** - Only requires first and second moment estimates

### Comparison to Other Methods

| Method | Adaptive LR | Momentum | Memory |
|--------|-------------|----------|--------|
| SGD | No | Optional | O(1) per param |
| Momentum | No | Yes | O(1) per param |
| AdaGrad | Yes | No | O(1) per param |
| RMSProp | Yes | No | O(1) per param |
| Adam | Yes | Yes | O(2) per param |

## Key Contributions

1. **Combined momentum and adaptivity** - Best of both worlds
2. **Theoretical convergence analysis** - Proved convergence under convex settings
3. **Robust defaults** - Works well with default hyperparameters
4. **Computational efficiency** - Minimal overhead

## Results

- **Convex optimization:** Faster convergence than AdaGrad and Momentum
- **Non-convex optimization:** Better than SGD, Momentum, AdaGrad on deep networks
- **NLP tasks:** State-of-the-art on word2vec training
- **Computer vision:** Competitive performance on ImageNet training
- **Reinforcement learning:** Works well for policy gradient methods

### Empirical Results

- **RMSProp:** Adam outperforms on non-stationary objectives
- **AdaGrad:** Adam better on sparse gradients
- **Momentum:** Adam better on noisy gradients
- **SGD:** Adam converges faster but may generalize worse

## Why It Matters

Adam became the default optimizer for deep learning:

1. **De facto standard** - Used in most deep learning applications
2. **Research default** - Many papers use Adam without justification
3. **Wide applicability** - Works across domains and architectures
4. **Inspired variants** - Led to many improved optimizers

## Weaknesses

- **Generalization** - May generalize worse than SGD with momentum
- **Memory** - Requires more memory than SGD
- **Hyperparameter sensitivity** - Default values don't always work
- **Non-stationary objectives** - Can be unstable on some problems

## Follow-up Work

- **AdamW:** Decoupled weight decay
- **RAdam:** Rectified Adam for better stability
- **LAMB:** Large batch training
- **LARS:** Layer-wise adaptive rates
- **Sophia:** Second-order optimizer