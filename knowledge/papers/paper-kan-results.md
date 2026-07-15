---
topic: papers
difficulty: hard
tags: [paper, kan, neural-networks, results, limitations]
last_sent:
review_count: 0
---

# KAN: Results, Grid Extension & Limitations

## Results

### Symbolic Function Fitting (5 examples)
- KAN[2,1,1]: 100% node accuracy on all 5 symbolic functions (f(x,y) = xy, exp(-(x²+y²)), etc.)
- MLP[2,200,200,1]: 0% accuracy (can not recover symbolic structure)
- MLP[2,200...1] even with sparsity: 0% accuracy

### Physics-Informed Learning (PDE solving)
- KAN achieves smaller L2 error than MLP with 100× fewer parameters on Poisson equation and Helmholtz equation
- Poisson: KAN[2,3,3,1]: L2 error 1.5×10⁻⁵ vs MLP[2,200,200,1]: 2.6×10⁻³

### Operator Learning (DeepONet-style)
- KAN-DeepONet: achieves 1.0×10⁻⁴ MSE vs DeepONet: 4.7×10⁻⁴ on antiderivative operator
- Requires 2.2M parameters vs 14.1M parameters for DeepONet

## Grid Extension (Key Feature)

KANs can be refined after training by increasing the number of B-spline knots (grid points). This enables progressive learning: train a small KAN first, then refine by adding grid points. The refinement preserves the existing function while increasing capacity.

**Refinement example:** Starting with G=3 (5 parameters per edge) → refining to G=10 (15 parameters per edge) without retraining from scratch. The fine-grained KAN maintains the behavior of the coarse KAN because B-splines are refinable (a coarse B-spline can be exactly represented on a finer grid).

## Limitations

1. **Training speed:** KANs are 3-10× slower to train than MLPs of comparable capacity due to multiple spline evaluations per edge
2. **Inference speed:** Similar overhead — B-spline evaluation is expensive compared to matrix multiply + ReLU
3. **Scalability:** Has not been demonstrated on large-scale tasks (ImageNet, language modeling)
4. **Optimization instability:** LBFGS is less stable than Adam for large models; batch training needs investigation
5. **GPU utilization:** B-spline evaluations do not map efficiently to GPU tensor cores
6. **Over-parameterization:** Each edge has multiple spline parameters, potentially leading to overfitting on small datasets

## Impact

KAN sparked significant interest as an alternative to MLPs for scientific computing and symbolic regression. However, as of early 2025, it remains a specialized architecture for small-scale, high-precision tasks rather than a general ML replacement. The theoretical connection to the Kolmogorov-Arnold theorem offers a principled foundation, but practical scaling challenges remain.

**Follow-up:** KAN 2.0 with convolution layers; KAN-tabular for structured data; and integration with transformer architectures where KAN replaces MLP in FFN layers.
