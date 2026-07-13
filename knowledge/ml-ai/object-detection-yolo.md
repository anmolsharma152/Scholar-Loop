---
difficulty: hard
last_sent: 2026-07-13 23:43:40.330462+00:00
review_count: 1
tags:
- cv
- yolo
- object-detection
topic: ml-ai
---

# Object Detection: YOLO and Beyond

Object detection localizes and classifies multiple objects in a single image. YOLO (You Only Look Once) revolutionized the field by framing detection as a single-pass regression problem, enabling real-time inference.

## Object Detection Fundamentals

Detection requires two outputs:
1. **Bounding box** $(x, y, w, h)$ — location and size
2. **Class label** — what object is in the box

| Architecture | Approach | Speed | Accuracy | Era |
|-------------|----------|-------|----------|-----|
| R-CNN family | Two-stage (propose + classify) | Slow | High | 2014-2016 |
| SSD | Single-stage (multi-scale) | Fast | Medium | 2016 |
| YOLO family | Single-stage (grid-based) | Very fast | High | 2016-present |
| DETR | Transformer-based | Medium | High | 2020-present |

## Intersection over Union (IoU)

IoU measures overlap between predicted and ground-truth bounding boxes:

$$\text{IoU} = \frac{\text{Area of Intersection}}{\text{Area of Union}} = \frac{|B_{pred} \cap B_{gt}|}{|B_{pred} \cup B_{gt}|}$$

IoU ≥ 0.5 is the standard threshold for a correct detection (COCO uses IoU ≥ 0.5:0.95 for mAP).

```python
def compute_iou(box1, box2):
    """Compute IoU between two boxes in (x1, y1, x2, y2) format."""
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    
    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = area1 + area2 - intersection
    
    return intersection / union if union > 0 else 0
```

## YOLO Architecture (Conceptual)

YOLO divides the image into an $S \times S$ grid. Each grid cell predicts:
- $B$ bounding boxes (each with $x, y, w, h, \text{confidence}$)
- $C$ class probabilities

Output tensor shape: $S \times S \times (B \times 5 + C)$

### Grid Cell Prediction

Each cell directly predicts bounding boxes and class probabilities simultaneously — no region proposal network needed.

```
Image → CNN Backbone → Grid Output (S×S×(B*5+C))
                      ↓
              Apply threshold + NMS
                      ↓
              Final detections
```

### Anchor Boxes

Instead of predicting arbitrary boxes, YOLOv2+ predicts offsets from predefined **anchor boxes** (priors):

$$b_x = \sigma(t_x) + c_x$$
$$b_y = \sigma(t_y) + c_y$$
$$b_w = p_w \cdot e^{t_w}$$
$$b_h = p_h \cdot e^{t_h}$$

where $(c_x, c_y)$ is the grid cell offset, $(p_w, p_h)$ is the anchor box dimensions, and $(t_x, t_y, t_w, t_h)$ are the network predictions.

### Non-Max Suppression (NMS)

Multiple cells may detect the same object. NMS removes redundant boxes:

1. Sort all detections by confidence score
2. Take the highest-confidence box
3. Remove all boxes with IoU > threshold (typically 0.5) with it
4. Repeat until no boxes remain

```python
def non_max_suppression(boxes, scores, iou_threshold=0.5):
    """boxes: (N, 4), scores: (N,)"""
    indices = scores.argsort(descending=True)
    keep = []
    
    while len(indices) > 0:
        current = indices[0]
        keep.append(current)
        
        if len(indices) == 1:
            break
        
        remaining = indices[1:]
        ious = torch.stack([compute_iou(boxes[current], boxes[i]) 
                           for i in remaining])
        indices = remaining[ious <= iou_threshold]
    
    return keep
```

## YOLO Evolution

| Version | Year | Key Innovation | mAP (COCO) | Speed |
|---------|------|----------------|------------|-------|
| YOLOv1 | 2016 | Grid-based single pass | 63.4 (VOC) | 45 FPS |
| YOLOv2 | 2016 | Batch norm, anchor boxes, multi-scale | 78.6 (VOC) | 40 FPS |
| YOLOv3 | 2018 | FPN, multi-scale predictions | 33.0 | 20 FPS |
| YOLOv4 | 2020 | CSPDarknet, Mosaic augmentation | 43.5 | 62 FPS |
| YOLOv5 | 2020 | PyTorch native, auto-anchor | 50.7 | 140 FPS |
| YOLOv8 | 2023 | Anchor-free, decoupled head | 53.9 | 100+ FPS |
| YOLOv9 | 2024 | GELAN, PGI | 55.6 | High |
| YOLOv10 | 2024 | NMS-free, consistent dual labels | 54.4 | Very high |

## R-CNN Family (For Comparison)

| Model | Proposal Method | Key Idea |
|-------|-----------------|----------|
| R-CNN | Selective Search | Extract regions → CNN features → SVM |
| Fast R-CNN | Selective Search (shared features) | ROI Pooling on shared feature map |
| Faster R-CNN | Region Proposal Network (RPN) | Learnable proposals, end-to-end |

R-CNN family is generally more accurate but slower than YOLO — used when accuracy matters more than speed.

## Loss Functions for Detection

Object detection typically combines multiple losses:

$$\mathcal{L} = \lambda_{box} \mathcal{L}_{box} + \lambda_{obj} \mathcal{L}_{obj} + \lambda_{cls} \mathcal{L}_{cls}$$

- **Box loss**: CIoU or GIoU loss for bounding box regression
- **Objectness loss**: Binary cross-entropy for object/no-object
- **Classification loss**: Cross-entropy for class labels

## Key Takeaways

- YOLO reframed detection as regression, enabling real-time performance
- IoU is the fundamental metric for bounding box accuracy
- Anchor boxes provide priors that make regression easier
- NMS eliminates duplicate detections
- Modern YOLO versions (v8+) are anchor-free and use decoupled heads
- mAP@0.5:0.95 (COCO) is the standard evaluation metric
- For deployment: YOLOv8 offers the best accuracy-speed tradeoff

## Common Bugs

| Bug | Symptom | Fix |
|-----|---------|-----|
| Wrong NMS threshold | Too many or too few detections | Tune per dataset (0.4-0.6 typical) |
| Not normalizing box coordinates | Training divergence | Normalize to [0, 1] relative to image size |
| Anchor box mismatch | Poor recall | Run k-means on training set anchors |
| Applying NMS across classes | Missing detections | Apply NMS per class |
| Forgetting to scale boxes to original image size | Wrong visualization | Multiply by `(img_w/input_w, img_h/input_h)` |
| Training on small images, testing on large | Poor small object detection | Use multi-scale training |