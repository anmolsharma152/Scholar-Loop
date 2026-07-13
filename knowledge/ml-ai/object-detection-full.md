---
topic: ml-ai
difficulty: hard
tags: [dl, detection, yolo, rcnn]
sources:
  - Object Detection in Depth.pdf (Masai)
  - Computer Vision: Tasks, Vision Transformer...pdf (Masai)
---

# Full Object Detection

## Task Hierarchy

1. **Image Classification**: Single label for whole image
2. **Classification + Localisation**: Label + bounding box `(x, y, W, H)` for one object
3. **Object Detection**: K classes + K bounding boxes (variable number)
4. **Instance Segmentation**: Class + pixel-level mask per object

## Bounding Box Regression

- Predict `b̂ = (x̂, ŷ, Ŵ, Ĥ)` — top-left corner + width/height
- **L2 loss**: `L_reg = ||b̂ - b*||²`
- **Class-specific**: C × 4 outputs (one box per class)
- **Class-agnostic**: 4 outputs (single box regardless of class)
- **Limitation**: Fixed output size means fixed number of objects

## IoU (Intersection over Union)

- `IoU(P, G) = |P ∩ G| / |P ∪ G|` ∈ [0, 1]
- IoU = 1.0: perfect overlap; IoU = 0: no overlap
- Threshold (typically 0.5) determines correct detection

## NMS (Non-Maximum Suppression)

1. Sort all detections by confidence score
2. Take highest-scored detection, suppress all with IoU > threshold
3. Repeat with remaining detections
4. Removes duplicate detections of same object

## Sliding Window Detection

- Apply fixed-size classifier at every spatial location, multiple scales, multiple aspect ratios
- **Problem**: 2000 candidates × 3 scales × 3 ratios = 18,000 forward passes (infeasible)
- **OverFeat solution**: Replace FC layers with 1×1 convolutions → single FCN forward pass covers all positions

## R-CNN Family

### R-CNN (CVPR 2014)

1. **Selective Search** generates ~2000 region proposals per image
2. Each region warped to fixed size, passed through CNN (AlexNet)
3. CNN features fed to SVM classifier + bounding box regressor
4. **Problem**: Extremely slow (47s/image), stores CNN features to disk

### Fast R-CNN (ICCV 2015)

1. CNN processes entire image once → feature map
2. RoI (Region of Interest) pooling extracts fixed-size features from each proposal
3. Single forward pass shared across all proposals
4. **Speedup**: 10-20× faster than R-CNN, 150× at test time

### Faster R-CNN (NeurIPS 2015)

1. **Region Proposal Network (RPN)**: Replaces Selective Search
2. RPN slides small network over feature map → proposes regions
3. **Anchor boxes**: Predefined boxes at each spatial position (multiple sizes/ratios)
4. End-to-end trainable: RPN + detection network share features
5. ~5 fps (near real-time)

### Mask R-CNN

- Extends Faster R-CNN with per-pixel mask prediction branch
- **RoI Align**: Fix quantization error in RoI pooling (bilinear interpolation)
- Outputs: class + bounding box + binary mask per instance

## Anchor Boxes

- Predefined reference boxes at each feature map location
- Multiple scales and aspect ratios per location (e.g., 3×3 = 9 anchors)
- Network predicts offsets from anchors: `b = (tx, ty, tw, th)` relative to anchor
- Matches objects to anchors by IoU during training

## One-Stage Detectors

### YOLO (You Only Look Once)

- Single-shot detection: entire image → grid → boxes + classes in one pass
- Image divided into S×S grid; each cell predicts B boxes + class probabilities
- **Advantage**: Very fast (real-time), global context
- **Limitation**: Struggles with small objects, many objects per cell

### SSD (Single Shot MultiBox Detector)

- Multi-scale feature maps for detecting different-sized objects
- Default anchor boxes at multiple resolutions
- Faster than two-stage, good accuracy/speed tradeoff

### RetinaNet

- **Focal loss**: Addresses class imbalance (foreground vs background)
- `FL(p_t) = -α_t(1-p_t)^γ log(p_t)` — downweights easy negatives
- ResNet backbone + Feature Pyramid Network (FPN)
- Matches two-stage detector accuracy at single-stage speed

## DETR (DEtection TRansformer)

- **Transformer-based**: No anchors, no NMS
- Set prediction: BIPARTITE MATCHING between predictions and ground truth
- Encoder processes CNN features; decoder generates object queries → predictions
- End-to-end, simple post-processing
- **Advantage**: Eliminates hand-designed components (anchors, NMS)
- **Limitation**: Slow convergence, struggles with small objects

## Evaluation Metrics

- **mAP (mean Average Precision)**: Average precision across all classes
  - AP = area under precision-recall curve for one class
  - mAP@0.5: IoU threshold of 0.5
  - mAP@[0.5:0.95]: Average over IoU thresholds (COCO standard)
- **Precision/Recall tradeoff**: Confidence threshold determines operating point
