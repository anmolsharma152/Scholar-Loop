---
topic: papers
difficulty: hard
tags: [paper, detr, object-detection, transformers]
last_sent:
review_count: 0
---

# DETR: End-to-End Object Detection with Transformers

**Authors:** Nicolas Carion, Francisco Massa, Gabriel Synnaeve, et al. (Facebook AI)
**Published:** ECCV 2020 (arXiv 2005.12872)

## Problem

Object detection pipelines had become complex, requiring many hand-designed components: anchor boxes, region proposal networks, NMS post-processing, and heuristic assignment of ground truth to proposals. These components each introduce hyperparameters that are difficult to tune and are not end-to-end differentiable.

**DETR eliminates:** anchor boxes, region proposal networks, non-maximum suppression, RoI pooling, and the complex multi-stage training that came with them.

## Key Idea

DETR frames object detection as a direct set prediction problem using a transformer encoder-decoder architecture. The decoder takes N learned "object queries" (learnable positional embeddings) as input and outputs N detection predictions. During training, a bipartite matching loss (Hungarian algorithm) assigns each ground truth object to exactly one prediction, so the model learns to output a permutation-invariant set of detections.

**Architecture:**
1. CNN backbone extracts feature map from image
2. Transformer encoder processes the flattened feature map with positional encodings
3. Transformer decoder attends to encoder output using N object queries (N=100)
4. FFN heads produce class + bounding box for each query

**Hungarian matching** finds the optimal one-to-one assignment between predictions and ground truth objects, maximizing precision and penalizing false positives. The loss is: L = L_class + L_box, where L_class is cross-entropy and L_box is L1 + generalized IoU loss.

## Key Contributions

1. First fully end-to-end object detector, no anchor boxes or NMS
2. Architecture can be extended to panoptic segmentation with minimal changes
3. Demonstrated that transformers can replace complex detection pipelines
4. Established a new paradigm for set prediction in computer vision
