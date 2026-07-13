---
topic: papers
difficulty: hard
tags: [paper, vision-transformer, vit, computer-vision, image-classification]
---

# An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale

**Authors:** Dosovitskiy et al. (Google Research)
**Published:** ICLR 2021
**arXiv:** 2010.11929

## Problem & Motivation

Transformers have achieved state-of-the-art in NLP, but convolutional neural networks (CNNs) still dominate computer vision. Questions remain:

1. Can pure Transformers work for vision without convolutions?
2. How do Transformers compare to CNNs at different scales?
3. What happens when Transformers are pre-trained on very large datasets?

The paper shows that a pure Transformer applied directly to sequences of image patches can perform very well on image classification when pre-trained on large datasets.

## Key Idea / Architecture

### Vision Transformer (ViT)

**Patch Embedding:**
- Split image into fixed-size patches (e.g., 16x16)
- Linearly embed each patch to dimension D
- Add learnable position embeddings
- Prepend a learnable [CLS] token

**Transformer Encoder:**
- Standard Transformer encoder (multi-head attention + FFN)
- Layer normalization applied before attention and FFN
- No convolution layers at all

**Classification Head:**
- Use [CLS] token output
- Linear classifier for final prediction

### Architecture Details

- Image size: 224x224
- Patch size: 16x16 → 196 patches + 1 [CLS] token = 197 tokens
- Embedding dimension: 768 (ViT-B), 1024 (ViT-L), 1280 (ViT-H)
- Number of layers: 12 (ViT-B), 24 (ViT-L), 32 (ViT-H)
- MLP ratio: 4 (hidden dimension = 4 * embedding dimension)

### Comparison to CNNs

| Model | Params | FLOPs | ImageNet (224) | ImageNet (384) |
|-------|--------|-------|----------------|----------------|
| ResNet-50 | 25M | 4G | 76.1% | - |
| ViT-B/16 | 86M | 17.6G | 77.9% | 84.0% |
| ViT-L/16 | 307M | 81.0G | 76.5% | 85.2% |
| ViT-H/14 | 632M | 167G | 88.5%* | 90.7%* |

*ViT-H/14 trained on JFT-300M

## Key Contributions

1. **Pure Transformer for vision** - No convolutions, just self-attention on patches
2. **Simple patch-based input** - Image patches treated like tokens in NLP
3. **Scale is crucial** - Transformers need more data than CNNs to generalize
4. **Pre-training on large datasets** - JFT-300M/3B enables strong performance

## Results

- **ImageNet (pre-trained on JFT-3B):** 88.55% top-1 accuracy (ViT-H/14)
- **ImageNet (from scratch):** 77.9% (ViT-B/16) - competitive with ResNet-50
- **CIFAR-10:** 99.50% accuracy
- **VTAB:** 84.07% average across 19 tasks

### Key Observations

1. **Data hunger** - ViT needs large datasets to outperform CNNs
2. **Pre-training matters** - Without pre-training, ViT underperforms CNNs
3. **Position embeddings learn spatial relationships** - Despite no explicit position encoding, model learns spatial structure
4. **Attention visualization** - Can interpret which patches the model attends to

## Why It Matters

ViT fundamentally changed computer vision:

1. **Unified architecture** - Same architecture for vision and NLP
2. **Foundation for multimodal models** - Vision-Language models use ViT
3. **Scaling laws for vision** - Showed benefits of scale in vision models
4. **Inspired efficient variants** - DeiT, Swin Transformer, etc.

## Weaknesses

- **Data hungry** - Needs massive pre-training datasets
- **Computational cost** - Self-attention is expensive for high-resolution images
- **Position embedding limitations** - Fixed position embeddings may not generalize to different resolutions
- **Lack of inductive bias** - No built-in translation invariance or locality

## Follow-up Work

- **DeiT:** Data-efficient training for Vision Transformers
- **Swin Transformer:** Hierarchical Transformer with shifted windows
- **BEiT:** Self-supervised pre-training for Vision Transformers
- **CLIP:** Joint vision-language pre-training using ViT