---
topic: papers
difficulty: hard
last_sent:
review_count: 0
tags:
  - paper
  - neural-networks
  - kolmogorov-arnold
  - splines
  - interpretability
---

# KAN: Kolmogorov-Arnold Networks

**Authors:** Ziming Liu, Yixuan Wang, Sachin Vaidya, Fabian Ruehle, James Halverson, Marin Soljacic, Thomas Y. Hou, Max Tegmark (MIT, Caltech, Northeastern)
**Published:** ICLR 2025
**arXiv:** 2404.19756

## Problem & Motivation

Multi-Layer Perceptrons (MLPs) are the foundational building blocks of deep learning, justified by the universal approximation theorem. However, MLPs have significant drawbacks: they consume almost all non-embedding parameters in transformers, are typically less interpretable (relative to attention layers), and are inefficient at approximating univariate functions due to fixed activation functions on nodes. The authors asked whether MLPs are truly the best nonlinear regressors, or whether a fundamentally different architecture grounded in the Kolmogorov-Arnold representation theorem could offer better accuracy and interpretability for scientific tasks. The Kolmogorov-Arnold theorem had been considered theoretically sound but practically useless in machine learning due to concerns about non-smooth inner functions. Previous attempts at KA networks were limited to the original depth-2, width-(2n+1) structure.

## Key Idea / Architecture

Kolmogorov-Arnold Networks (KANs) are inspired by the Kolmogorov-Arnold representation theorem, which states that any multivariate continuous function can be decomposed into a finite composition of continuous univariate functions and addition. The key architectural change: while MLPs have fixed activation functions on nodes (neurons) and learnable linear weights on edges, KANs have learnable activation functions on edges and simple summation on nodes. KANs have no linear weight matrices at all—every weight parameter is replaced by a univariate function parameterized as a B-spline.

```
KAN layer: x_{l+1,j} = sum_i phi_{l,j,i}(x_{l,i})
MLP layer: x_{l+1} = W_l * sigma(x_l)
```

Each activation function phi(x) is parameterized as a sum of a residual basis function (SiLU) and a B-spline: `phi(x) = w_b * b(x) + w_s * spline(x)`. The spline is a linear combination of B-spline basis functions with learnable coefficients. KAN layers are generalized to arbitrary width and depth by stacking multiple layers, where each layer is a matrix of 1D functions. The grid points of B-splines are updated on the fly during training to handle evolving input ranges. Pruning and grid extension techniques are provided to make KANs increasingly accurate and interpretable. The neural scaling law for KANs achieves exponent alpha = k+1 (where k is spline order), compared to MLPs which struggle to saturate even alpha = 1.

## Key Contributions

1. Proposed KANs as a principled alternative to MLPs, placing learnable spline-based activation functions on edges instead of fixed activations on nodes
2. Showed theoretically and empirically that KANs possess faster neural scaling laws than MLPs (alpha = 4 for cubic splines vs. alpha <= 2 for MLPs)
3. Demonstrated that smaller KANs can achieve comparable or better accuracy than larger MLPs in function fitting tasks
4. Established KANs as interpretable "collaborators" for scientific discovery, successfully (re)discovering mathematical and physical laws
5. Provided practical implementation with network simplification, pruning, and grid extension techniques
6. Generalized the original Kolmogorov-Arnold theorem (depth-2, width-2n+1) to arbitrary widths and depths, making it practical for modern deep learning

## Results (Specific Numbers)

- KAN (2,5,1) with 313 params beats MLP (2,20,1) with 881 params on fitting f(x1,...,x5) = exp(sum(sin^2(xi)))
- KAN scaling exponent alpha = 4 for k=3 (cubic) splines, vs. MLPs plateauing around alpha = 1
- Knot theory experiment: KAN discovered correct formula with high accuracy using grid extension from G=5 to G=200
- Anderson localization: KAN correctly identified the phase transition formula from data
- KAN-5 with shape [2,5,1] achieves RMSE of 10^-3 on a 2-variable function with only 50 grid points
- On a toy physics problem, KAN [2,5,1] achieves 10^-5 RMSE with 313 parameters while MLP (2,5,1) achieves only 10^-2 with 581 parameters

## Why It Matters / Impact

KANs challenge the dominance of MLPs as the default nonlinear function approximator in deep learning. By combining the compositional structure learning of MLPs with the high accuracy of spline approximation in low dimensions, KANs offer a path toward models that are simultaneously more accurate and more interpretable—particularly valuable for AI-for-science applications where understanding the learned function matters. The faster scaling laws suggest KANs could achieve the same accuracy with far fewer parameters, though this advantage may diminish at very large scales. The interpretability properties of KANs, where learned functions can be directly visualized and pruned, make them especially promising for scientific discovery where model transparency is essential.

## Weaknesses / Limitations

- Current experiments are limited to small-scale AI + science tasks; scaling KANs to transformer-level sizes remains unexplored
- Training time per step is slower than MLPs due to spline computation and grid updates (grids updated on the fly during training)
- The curse of dimensionality is only beaten when smooth compositional structures exist in the data; worst-case functions may still require exponential resources
- No established training recipes or ecosystem comparable to MLPs, limiting practical adoption
- The theoretical guarantee assumes smooth Kolmogorov-Arnold representations, which may not exist for all functions of practical interest
- B-spline implementation adds memory overhead: each activation function stores G + k coefficients per spline
- Grid extension technique increases accuracy but also increases computation and parameter count
- Residual basis function (SiLU) is added to spline output to ensure activations don't start from zero

## Follow-up Work

- KAN-based PDE solvers: extending KANs to physics-informed neural networks for scientific computing
- Temporal KANs: applying spline-based activations to time-series and sequence modeling
- Vision KANs: exploring KAN layers as drop-in replacements for MLPs in vision transformers
- Scaling studies: investigating whether KAN advantages persist at billion-parameter scales
- KAN-GCN: combining KANs with graph convolutional networks for molecular and social network analysis
- pykan library: open-source implementation at github.com/KindXiaoming/pykan, installable via pip
- Grid extension from G=5 to G=200 increased accuracy by orders of magnitude in knot theory experiment
- Weighted residual basis functions added to spline output for numerical stability
- KAN layers use approximately 20% more computation per parameter than MLPs due to spline evaluation overhead

---
