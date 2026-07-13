---
topic: ml-ai
difficulty: medium
tags: [dl, fundamentals, backpropagation]
sources:
  - DeepLearning101.pdf
  - DeepLearning102.pdf
  - DeepLearning103.pdf
  - DeepLearning104.pdf
  - LossFunction.pdf
---

# Deep Learning 101 — Foundations

## Perceptron & MLP

- **Perceptron**: Single neuron computes `Wx + b`, fires if output exceeds threshold
- **MLP (Multi-Layer Perceptron)**: Stack of fully-connected layers; each neuron aggregates weighted inputs, adds bias, applies activation
- Linear equation in matrix form: `Y = Wx` (or `Y = Wx + b` where b is bias)
- A neuron works as an aggregator: computes `W₀ + Σwᵢxᵢ`, fires if result is above threshold

## Derivatives & Optimization Motivation

- Derivative `dy/dx` = rate of change; "how much does Y change when X changes"
- Think of weights as knobs — derivatives tell us how much each knob affects the output
- **Univariate**: function plotted in 2D, differentiate in one direction
- **Multivariate**: function in 3D+, partial derivatives `∂y/∂xᵢ` for each variable
- **Minimization**: Find `x` where `dy/dx = 0`; second derivative determines maxima vs minima
- **Loss landscape**: Given a multidimensional function F over param space, find `argmin_W F(W)` via gradient descent

## Backpropagation & Chain Rule

- Backpropagation applies the chain rule to compute gradients layer by layer from output back to input
- For a composite function `f(g(x))`, derivative is `f'(g(x)) · g'(x)`
- Gradient of loss w.r.t. each weight tells how to update it: `w ← w - η · ∂L/∂w`
- Computation graph allows efficient backward pass via dynamic programming

## Activation Functions

| Function | Formula | Properties |
|----------|---------|------------|
| **Sigmoid** | `σ(x) = 1/(1+e⁻ˣ)` | Output (0,1), vanishing gradients at extremes |
| **Tanh** | `tanh(x)` | Output (-1,1), zero-centered but still vanishes |
| **ReLU** | `max(0,x)` | Fast, sparse activation, dying ReLU problem |
| **GELU** | `x · Φ(x)` | Smooth approximation of ReLU, used in Transformers |
| **Swish** | `x · σ(βx)` | Self-gated, smooth, slight negative region |

## Vanishing & Exploding Gradients

- **Vanishing**: Gradients shrink exponentially through deep sigmoid/tanh layers; early layers learn negligibly
- **Exploding**: Gradients grow exponentially, especially in RNNs with large weight matrices
- **Solutions**: ReLU activations, batch normalization, residual connections (ResNet), careful initialization

## Weight Initialization

- **Xavier/Glorot**: `W ~ N(0, 2/(fan_in + fan_out))` — keeps variance stable across layers; best for sigmoid/tanh
- **He/Kaiming**: `W ~ N(0, 2/fan_in)` — accounts for ReLU halving the variance; default for ReLU networks
- Proper initialization prevents activations from becoming too large or too small in early training

## Loss Functions (from DL4All)

- **MSE (L2)**: `Σ(y - ŷ)²` — penalizes large errors heavily, used for regression
- **MAE (L1)**: `Σ|y - ŷ|` — Manhattan distance, more robust to outliers
- **Huber Loss**: Best of both — MSE near origin, MAE far from origin
- **Cross-Entropy**: Natural loss for classification; `CE = -Σ yᵢ log(ŷᵢ)`
- **Why CE over MSE for classification**: MSE does not penalize misclassification as strongly; CE gradient is stronger for confident wrong predictions
- **Softmax + CE**: Combined form simplifies gradient to `ŷ - y` (predicted probability minus one-hot target)

## Key Equations

```
Neuron:          y = f(Wx + b)
MSE Loss:        L = (1/n) Σ(yᵢ - ŷᵢ)²
Cross-Entropy:   L = -Σ yᵢ log(ŷᵢ)
Gradient Descent: w ← w - η · ∂L/∂w
Xavier Init:     W ~ N(0, 2/(n_in + n_out))
He Init:         W ~ N(0, 2/n_in)
```
