---
topic: papers
difficulty: hard
tags: [paper, resnet, residual-learning, deep-networks, computer-vision]
---

# Deep Residual Learning for Image Recognition

**Authors:** He, Zhang, Ren, Sun (Microsoft Research)
**Published:** CVPR 2016
**arXiv:** 1512.03385

## Problem & Motivation

Deep neural networks are hard to train. As networks get deeper:
1. **Degradation problem** - Training error increases with depth (not just test error)
2. **Vanishing/exploding gradients** - Gradients become very small or large in deep networks
3. **Harder optimization** - Deeper models should be at least as good as shallower ones, but empirically they're worse

The degradation problem suggests that deep models have difficulty learning identity mappings - it's easier to learn residual functions than to learn direct mappings.

## Key Idea / Architecture

### Residual Learning

Instead of learning $H(x)$ directly, learn the residual $F(x) = H(x) - x$. Then:

$$H(x) = F(x) + x$$

This is the "skip connection" or "shortcut connection" - it makes the identity mapping trivial to learn.

### Residual Block

```
x → Conv → BN → ReLU → Conv → BN → (+x) → ReLU
```

The shortcut connection adds x before the final ReLU. If dimensions don't match (for downsampling), a learned projection is used:

$$y = F(x, \{W_i\}) + W_s x$$

### Network Architectures

- **ResNet-34:** 34 layers with residual blocks
- **ResNet-50:** 50 layers with bottleneck blocks
- **ResNet-101:** 101 layers
- **ResNet-152:** 152 layers

### Bottleneck Design (for deeper networks)

For efficiency, use 1x1 → 3x3 → 1x1 convolutions:
- First 1x1 reduces dimensions
- 3x3 operates on reduced dimensions
- Second 1x1 restores dimensions

## Key Contributions

1. **Residual learning** - Simple but powerful idea of learning residuals
2. **Enables very deep networks** - Successfully trains 152-layer networks (8x deeper than VGG)
3. **Ease of optimization** - Deeper networks actually have lower training error
4. **Feature reuse** - Skip connections allow features from earlier layers to be used directly

## Results

- **ImageNet 2015:** Won first place (3.57% top-5 error)
- **COCO detection:** 27.7% mAP (improvement of ~6% over previous best)
- **COCO segmentation:** Improves by 4% over previous best
- **152-layer ResNet:** 3.57% top-5 error on ImageNet
- **Training efficiency:** 152-layer ResNet trains faster than 34-layer plain network

### Key Observations

1. **Deeper is better** - 152-layer outperforms 34-layer significantly
2. **Identity shortcuts are sufficient** - Learned projections not needed for most cases
3. **Feature reuse** - Deeper layers can use features from earlier layers
4. **Generalization** - Residual learning helps both training and test performance

## Why It Matters

ResNet became the foundation of modern deep learning:

1. **Enabled deep learning revolution** - Made training very deep networks practical
2. **Foundation architecture** - Used as backbone for detection, segmentation, etc.
3. **Concept of skip connections** - Influenced many subsequent architectures (DenseNet, U-Net)
4. **Pre-training backbone** - ResNet-50/101 became standard pre-trained models

## Weaknesses

- **Still limited depth** - 152 layers is practical, but going much deeper shows diminishing returns
- **Computational cost** - Very deep networks are expensive to train and deploy
- **Not optimal for all tasks** - Some tasks may benefit from different architectures

## Follow-up Work

- **DenseNet:** Dense connections instead of residual connections
- **ResNeXt:** Grouped convolutions with residual connections
- **SE-ResNet:** Squeeze-and-excitation for channel attention
- **Vision Transformers:** Transformers replaced ResNets as the dominant vision architecture