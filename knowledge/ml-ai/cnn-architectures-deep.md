---
topic: ml-ai
difficulty: medium
tags: [dl, cnn, architectures]
sources:
  - DeepLearning102.pdf
  - DeepLearning103.pdf
  - DeepLearning104.pdf
  - Computer Vision: Tasks, Vision Transformer (ViT)...pdf (Masai)
---

# Deep CNN Architectures Beyond Basics

## Convolution Basics Review

- Convolution = pixel-level operator computed with neighborhood
- `R(x,y) = Σ_k Σ_l F(k,l) · I(x-k, y-l)` — filter slides over input computing dot products
- Filters detect specific patterns: edges (directional derivatives), textures, shapes
- Questions embedded in filters: "What is your gradient?", "Do you belong to a horizontal line?", "Do you have this pattern?"

## VGG (Visual Geometry Group)

- **Key insight**: Depth matters — use many 3×3 convolutions stacked
- All convolutions are 3×3 with stride 1, padding 1
- Max pooling 2×2 stride 2 doubles channels each block
- Architectures: VGG-16 (13 conv + 3 FC), VGG-19 (16 conv + 3 FC)
- **Limitation**: Large number of parameters (138M for VGG-16) due to FC layers

## Inception (GoogLeNet)

- **Inception module**: Apply multiple filter sizes in parallel, concatenate
  - 1×1 conv, 3×3 conv, 5×5 conv, 3×3 max pool → all concatenated
- **1×1 convolutions**: Reduce channel dimension before expensive 3×3/5×5 convs (bottleneck)
  - Example: 256 channels → 64 via 1×1 conv → 3×3 conv on 64 → expand back
  - Dramatically reduces computation
- **Network in Network**: 1×1 conv adds non-linearity without spatial dimension change
- GoogLeNet: 22 layers, ~5M parameters (12× smaller than AlexNet)

## ResNet (Residual Networks)

- **Residual/skip connections**: `y = F(x) + x` — learn residual rather than full mapping
- **Bottleneck block** (ResNet-50+): 1×1 → 3×3 → 1×1 with skip connection
  - 1×1 reduces dimensions, 3×3 operates on small dimension, 1×1 restores
- Enables training of 50, 101, 152+ layer networks
- **Why it works**: Gradient flows directly through identity shortcut; solves vanishing gradients in deep networks
- Degradation problem solved: deeper networks can at worst match shallower performance (residual = 0)

## DenseNet (Densely Connected Networks)

- **Dense connectivity**: Each layer receives feature maps from ALL previous layers
- `x_l = H_l([x_0, x_1, ..., x_{l-1}])` — concatenation of all preceding features
- **Growth rate k**: Each layer adds k new feature maps
- **Bottleneck layers**: 1×1 conv before 3×3 to reduce input channels
- Benefits: feature reuse, reduced parameters, stronger gradient flow
- DenseNet-121: ~8M parameters (vs VGG-16's 138M)

## EfficientNet (Compound Scaling)

- **Compound scaling**: Uniformly scale width, depth, and resolution together
- `depth: d = α^φ`, `width: w = β^φ`, `resolution: r = γ^φ`
- Constraint: `α · β² · γ² ≈ 2` (FLOPS constraint)
- Found via neural architecture search (NAS)
- EfficientNet-B0 to B7: B0 is baseline, each variant scales up
- **Depthwise separable convolutions**: Factorize spatial and channel operations

## MobileNet & Xception (Depthwise Separable Convolutions)

- **Standard convolution**: Filter operates on all input channels simultaneously
- **Depthwise separable**: Split into two cheaper operations
  1. **Depthwise conv**: Single filter per input channel (spatial mixing only)
  2. **Pointwise conv**: 1×1 conv to combine channels (channel mixing only)
- **Cost reduction**: ~k² reduction where k is kernel size (typically 8-9× cheaper)
- **MobileNet**: Depthwise separable convs + width multiplier + resolution multiplier
- **Xception**: Extreme Inception — depthwise separable as core building block

## Architecture Comparison

| Architecture | Depth | Parameters | Key Innovation |
|-------------|-------|------------|----------------|
| VGG-16 | 16 | 138M | Uniform 3×3 convolutions |
| Inception | 22 | 5M | Multi-scale parallel filters + 1×1 bottlenecks |
| ResNet-50 | 50 | 25M | Skip/residual connections |
| DenseNet-121 | 121 | 8M | Dense connectivity, feature reuse |
| EfficientNet-B0 | — | 5.3M | Compound scaling + NAS |
| MobileNet | — | 4.2M | Depthwise separable convolutions |
