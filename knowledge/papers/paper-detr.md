---
topic: papers
difficulty: hard
last_sent:
review_count: 0
tags:
  - paper
  - object-detection
  - transformer
  - end-to-end
  - bipartite-matching
  - coco
  - set-prediction
---

# End-to-End Object Detection with Transformers (DETR)

**Authors:** Nicolas Carion, Francisco Massa, Gabriel Synnaeve, Nicolas Usunier, Alexander Kirillov, Sergey Zagoruyko (Facebook AI)
**Published:** ECCV 2020
**arXiv:** 2005.12872v3

## Problem & Motivation

Modern object detection relies on indirect set prediction through surrogate regression and classification tasks on large sets of proposals or anchors. Performance is heavily influenced by post-processing steps like non-maximum suppression (NMS), anchor design, and heuristic target assignment rules. These hand-designed components encode prior knowledge about the task and create complex pipelines that are difficult to optimize end-to-end. Previous attempts at direct set prediction either added other forms of prior knowledge or had not proven competitive with strong baselines on challenging benchmarks. The goal was to view object detection as a direct set prediction problem, removing NMS and anchor heuristics entirely.

## Key Idea / Architecture

### Transformer Encoder-Decoder

DETR uses a transformer encoder-decoder architecture to directly predict a fixed-size set of N=100 bounding boxes in parallel. A CNN backbone (ResNet-50 or ResNet-101) generates a feature map f with C=2048 channels at H/32 x W/32 resolution. A 1x1 convolution reduces channel dimension to d=256. The encoder collapses spatial dimensions into a sequence and applies multi-head self-attention with fixed sine positional encodings added at each attention layer. The decoder takes N learned object queries (input positional embeddings) and attends to encoder output via self-attention and encoder-decoder attention, producing N output embeddings decoded in parallel.

### Prediction Heads

Each decoder output is passed to a shared 3-layer FFN with ReLU activation (hidden dimension d=256) and a linear projection layer. The FFN predicts normalized box coordinates (center, height, width) w.r.t. the input image. The linear layer predicts class labels via softmax, including a special "no object" class.

### Bipartite Matching Loss (Hungarian Loss)

Training finds the optimal one-to-one assignment between predicted and ground-truth objects using the Hungarian algorithm. The matching cost is:

L_match(y_i, y_hat_sigma(i)) = -1{c_i != empty} * p_hat(c_i) + 1{c_i != empty} * L_box(b_i, b_hat)

The Hungarian loss adds negative log-likelihood for classification plus box regression losses. L_box is a linear combination of L1 loss and generalized IoU (GIoU) loss, scale-invariant. The "no object" class is down-weighted by factor 10 to handle class imbalance. Auxiliary losses are applied after each decoder layer with shared prediction FFN parameters.

## Key Contributions

1. Views object detection as direct set prediction via bipartite matching loss, eliminating NMS and anchor heuristics
2. Transformer encoder-decoder with parallel decoding for global reasoning over object relationships
3. Competitive results with Faster R-CNN on COCO (42 AP vs 42.0 AP with same parameter count)
4. Significantly better performance on large objects (+7.8 APL), generalizes easily to panoptic segmentation

## Results (Specific Numbers)

### COCO Val Performance

| Model | GFLOPS/FPS | Params | AP | AP50 | AP75 | APS | APM | APL |
|-------|-----------|--------|-----|------|------|-----|-----|-----|
| Faster R-CNN-FPN+ (R50) | 180/26 | 42M | 42.0 | 62.1 | 45.5 | 26.6 | 45.4 | 53.4 |
| Faster R-CNN-R101-FPN+ | 246/20 | 60M | 44.0 | 63.9 | 47.8 | 27.2 | 48.1 | 56.0 |
| DETR (R50) | 86/28 | 41M | 42.0 | 62.4 | 44.2 | 20.5 | 45.8 | 61.1 |
| DETR-DC5 (R50) | 187/12 | 41M | 43.3 | 63.1 | 45.9 | 22.5 | 47.3 | 61.1 |
| DETR-R101 | 152/20 | 60M | 43.5 | 63.8 | 46.4 | 21.9 | 48.0 | 61.8 |
| DETR-DC5-R101 | 253/10 | 60M | 44.9 | 64.7 | 47.7 | 23.7 | 49.5 | 62.3 |

### Key Observations

- DETR achieves 42 AP with 41M parameters vs Faster R-CNN-FPN 42 AP with 42M parameters
- Large object AP: DETR 61.1 vs Faster R-CNN 53.4 (+7.7 improvement from non-local transformer attention)
- Small object AP: DETR 20.5 vs Faster R-CNN 26.6 (-6.1, a significant weakness)
- Training: 500 epochs on 16 V100 GPUs, batch size 64, ~3 days for 300-epoch ablation schedule
- Encoder ablation: 0 encoder layers -> 36.7 AP (-3.9); 12 encoder layers -> 41.6 AP
- Decoder ablation: Each decoder layer adds ~1.3 AP; total +8.2 AP from first to last layer
- NMS unnecessary: NMS helps first decoder layer predictions but hurts final layers

## Why It Matters / Impact

DETR fundamentally changed object detection by proving that transformer-based direct set prediction can match highly-optimized two-stage detectors without any hand-designed components like NMS or anchors. The simplicity of the approach (implementable in fewer than 50 lines of PyTorch inference code) lowered the barrier for researchers. The success of bipartite matching loss for detection influenced subsequent work including Deformable DETR, DAB-DETR, and DINO. The architecture extended naturally to panoptic segmentation, demonstrating generality.

## Weaknesses / Limitations

- Significantly worse performance on small objects (-6.1 AP on APS vs Faster R-CNN)
- Requires extra-long training schedule (500 epochs vs typical 36 for Faster R-CNN)
- Fixed set of N=100 queries means many predictions are "no object" for images with few objects
- Does not easily incorporate scale-specific features like FPN
- Lower AP50 (62.4) compared to some Faster R-CNN variants (63.9)

## Follow-up Work / Key References

- Deformable DETR (Zhu et al., 2021) — deformable attention modules addressing small object weakness
- DAB-DETR (Liu et al., 2022) — dynamic anchor boxes for better query initialization
- DINO (Zhang et al., 2022) — contrastive denoising training, achieves 63.3 AP on COCO
- MaskFormer / Mask2Former — extending DETR paradigm to panoptic and instance segmentation
- Faster R-CNN (Ren et al., 2015) — the baseline detector DETR was compared against
- Hungarian Algorithm (Kuhn, 1955) — used for bipartite matching in the loss
