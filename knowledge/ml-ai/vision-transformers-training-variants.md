---
difficulty: hard
tags: [cv, vit, transformer, variants]
topic: ml-ai
last_sent:
review_count: 0
---

# Vision Transformers: Training, Data & Variants

## Why ViT Needs More Data

CNNs have built-in **inductive bias**: locality (small kernels look at local regions) and translation equivariance (same filter everywhere). ViT has neither — self-attention is global from the first layer.

| Architecture | Data Required | Why |
|---|---|---|
| CNN (ResNet) | ~1M images (ImageNet) | Built-in spatial inductive biases |
| ViT (B/16) | ~14M+ images | Must learn spatial relationships from data |
| ViT (L/14) | ~300M+ images (JFT-300M) | Large models need more data |

With enough data, ViT's lack of inductive bias becomes an advantage — it can learn more flexible representations than CNNs.

## DINO (Self-Distillation with No Labels)

DINO (Caron et al., 2021) pre-trains ViT without labels using self-distillation:

1. Two networks: student and teacher (momentum-updated copy of student)
2. Both receive different augmentations of the same image
3. Teacher's output (with centering) is the target
4. Student minimizes cross-entropy with teacher's output

**Key finding:** DINO-trained ViT attention maps spontaneously learn semantic segmentation — attending to object boundaries without any labels. This suggests transformers learn meaningful visual representations through self-supervision.

## Hybrid CNN-Transformer Architectures

Combine CNN feature extraction with transformer reasoning:

| Model | CNN Stage | Transformer Stage | Benefit |
|---|---|---|---|
| CoAT | Stem + MBConv | Transformer blocks | Gradual transition |
| CvT | Conv projection | Transformer | Reduced computation |
| Swin | Patch partition + CNN-like | Shifted window attention | Hierarchical features |

Hybrid models often outperform pure ViT on small datasets by leveraging CNN inductive biases early.

## ViT Variants

| Model | Layers | Embed Dim | Heads | Params | ImageNet Top-1 |
|---|---|---|---|---|---|
| ViT-B/16 | 12 | 768 | 12 | 86M | 84.2% |
| ViT-L/16 | 24 | 1024 | 16 | 307M | 85.2% |
| ViT-H/14 | 32 | 1280 | 16 | 632M | 88.6% |
| DeiT-S/16 | 12 | 384 | 6 | 22M | 81.8% (distilled) |

DeiT (Data-efficient Image Transformer) introduced distillation tokens to train ViT effectively on ImageNet alone.

## Key Takeaways

- ViT treats images as sequences of patches, applying standard transformer architecture
- Patch size determines resolution: smaller patches = more tokens = higher resolution but more computation
- ViT lacks CNN inductive biases, requiring more training data
- For limited data: use hybrid architectures or data-efficient training (DeiT)
- For large-scale: pure ViT scales better than CNNs with more data
