---
difficulty: easy
last_sent:
review_count: 0
tags:
  - cv
  - computer-vision
topic: ml-ai
---

# Computer Vision Fundamentals

Computer vision (CV) is the field of enabling machines to interpret and understand visual information from images and videos. This note covers the foundational concepts: image representation, convolutions, pooling, and data augmentation.

## Image Representation

An image is a grid of pixel values:

| Format | Description | Shape (H×W×C) | Use Case |
|--------|-------------|----------------|----------|
| Grayscale | Single intensity channel | (H, W, 1) | Edge detection, simple tasks |
| RGB | Red, Green, Blue channels | (H, W, 3) | Standard color images |
| RGBA | RGB + Alpha (transparency) | (H, W, 4) | Compositing, overlays |
| HSV | Hue, Saturation, Value | (H, W, 3) | Color-based segmentation |

Pixel values range from 0-255 (uint8) or 0.0-1.0 (float). Models typically normalize to zero mean and unit variance.

```python
import numpy as np
from PIL import Image

img = np.array(Image.open("photo.jpg"))
print(img.shape)   # (480, 640, 3) — height, width, channels
print(img.dtype)   # uint8
print(img.min(), img.max())  # 0, 255

# Normalize for model input
img_float = img.astype(np.float32) / 255.0
mean = np.array([0.485, 0.456, 0.406])  # ImageNet mean
std = np.array([0.229, 0.224, 0.225])   # ImageNet std
img_normalized = (img_float - mean) / std
```

## The Convolution Operation

Convolution slides a small **filter** (kernel) across the image, computing dot products at each position to produce a **feature map**.

A 3×3 edge-detection kernel:
```
[[ 1,  0, -1],
 [ 1,  0, -1],
 [ 1,  0, -1]]
```

Key convolution parameters:

| Parameter | Description | Effect |
|-----------|-------------|--------|
| Kernel size | Spatial extent (3×3, 5×5, 7×7) | Larger = more receptive field |
| Stride | Step size | Stride 2 = downsample by 2× |
| Padding | Border pixels added | "same" preserves spatial size |
| Dilation | Spacing between kernel elements | Increases receptive field without more params |
| Channels | Number of filters | More filters = richer features |

Output size: $O = \lfloor\frac{W - K + 2P}{S}\rfloor + 1$

where $W$ = input width, $K$ = kernel size, $P$ = padding, $S$ = stride.

```python
import torch.nn as nn

conv = nn.Conv2d(
    in_channels=3,     # RGB input
    out_channels=64,   # 64 different filters
    kernel_size=3,     # 3×3 kernel
    stride=1,
    padding=1          # "same" padding for 3×3
)
# Input: (batch, 3, H, W) → Output: (batch, 64, H, W)

x = torch.randn(1, 3, 224, 224)
out = conv(x)
print(out.shape)  # torch.Size([1, 64, 224, 224])
```

## Feature Maps

Each filter learns to detect a specific pattern:
- **Early layers**: Edges, corners, textures
- **Middle layers**: Shapes, patterns, parts of objects
- **Deep layers**: Object-level features (faces, wheels, eyes)

This hierarchy of features is what makes CNNs powerful — they automatically learn relevant representations.

## Pooling

Pooling reduces spatial dimensions, providing translation invariance and reducing computation:

| Type | Operation | Effect |
|------|-----------|--------|
| Max Pooling | Takes maximum value in window | Preserves strongest feature |
| Average Pooling | Takes mean value in window | Smooths features |
| Global Average Pooling | Average over entire feature map | Replaces fully-connected layer |

```python
pool = nn.MaxPool2d(kernel_size=2, stride=2)
# (batch, 64, 224, 224) → (batch, 64, 112, 112)

gap = nn.AdaptiveAvgPool2d(output_size=(1, 1))
# (batch, 64, 224, 224) → (batch, 64, 1, 1) — useful before classifier
```

## Image Augmentation

Data augmentation artificially increases training set diversity by applying random transformations:

| Augmentation | Transform | Why |
|--------------|-----------|-----|
| Horizontal flip | Mirror left-right | Orientation invariance |
| Random crop | Crop random region | Scale/location invariance |
| Rotation | Rotate by random angle | Rotation invariance |
| Color jitter | Vary brightness, contrast, saturation, hue | Lighting invariance |
| Random erasing | Mask random patches | Occlusion robustness |
| Gaussian blur | Apply blur kernel | Focus on structure, not texture |

```python
from torchvision import transforms

train_transform = transforms.Compose([
    transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, 
                           saturation=0.2, hue=0.1),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], 
                         [0.229, 0.224, 0.225]),
])

val_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], 
                         [0.229, 0.224, 0.225]),
])
```

Note: augmentation is applied only during training, never during validation/testing.

## Key Takeaways

- Images are tensors of shape (C, H, W); normalization to ImageNet statistics is standard
- Convolution detects local features; stacking convolutions builds hierarchical representations
- Pooling reduces spatial dimensions and adds translation invariance
- Data augmentation is critical for preventing overfitting and improving generalization
- Modern CNNs (ResNet, EfficientNet) follow the pattern: Conv → BatchNorm → ReLU → Pool → Repeat
- Understanding receptive fields helps design deeper networks

## Common Bugs

| Bug | Symptom | Fix |
|-----|---------|-----|
| Wrong channel order (RGB vs BGR) | Colors look wrong | Verify library's expected order |
| Normalizing with wrong mean/std | Poor convergence | Use dataset-appropriate statistics |
| Applying augmentation at test time | Inconsistent predictions | Only augment training data |
| Padding that changes spatial size unexpectedly | Shape mismatches | Use `padding=kernel_size // 2` for "same" |
| Not moving model/data to same device | CUDA errors | Ensure `model.to(device)` and `x.to(device)` |
