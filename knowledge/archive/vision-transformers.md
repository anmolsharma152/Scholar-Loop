---
difficulty: hard
last_sent:
review_count: 0
tags:
  - cv
  - vit
  - transformer
topic: ml-ai
---

# Vision Transformers (ViT)

Vision Transformers apply the transformer architecture directly to images, replacing convolutional layers entirely. ViT demonstrated that transformers can match or exceed CNNs on vision tasks when given sufficient data.

## From Sequence to Patch: ViT Architecture

ViT (Dosovitskiy et al., 2020) treats an image as a sequence of patches:

1. **Split image into patches**: Reshape image of size $(H, W, C)$ into $N = \frac{H \times W}{P^2}$ patches of size $(P \times P \times C)$
2. **Linear projection**: Map each patch to a $D$-dimensional embedding
3. **Add positional encoding**: Inject spatial information (patches have no inherent order)
4. **Prepend CLS token**: Learnable token whose final representation is used for classification
5. **Pass through transformer encoder**: Standard self-attention + FFN blocks
6. **Classify from CLS token**: Use final CLS embedding for prediction

```python
import torch
import torch.nn as nn

class PatchEmbedding(nn.Module):
    def __init__(self, img_size=224, patch_size=16, in_channels=3, embed_dim=768):
        super().__init__()
        self.num_patches = (img_size // patch_size) ** 2
        self.proj = nn.Conv2d(in_channels, embed_dim, 
                              kernel_size=patch_size, stride=patch_size)
    
    def forward(self, x):
        # x: (batch, 3, 224, 224) → (batch, embed_dim, 14, 14)
        x = self.proj(x)
        # → (batch, embed_dim, 196) → (batch, 196, embed_dim)
        x = x.flatten(2).transpose(1, 2)
        return x

class ViT(nn.Module):
    def __init__(self, img_size=224, patch_size=16, in_channels=3,
                 num_classes=1000, embed_dim=768, num_layers=12,
                 num_heads=12, dropout=0.1):
        super().__init__()
        self.patch_embed = PatchEmbedding(img_size, patch_size, 
                                          in_channels, embed_dim)
        num_patches = self.patch_embed.num_patches
        
        self.cls_token = nn.Parameter(torch.randn(1, 1, embed_dim))
        self.pos_embed = nn.Parameter(torch.randn(1, num_patches + 1, embed_dim))
        self.dropout = nn.Dropout(dropout)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim, nhead=num_heads, 
            dim_feedforward=embed_dim * 4, dropout=dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, 
                                                 num_layers=num_layers)
        self.norm = nn.LayerNorm(embed_dim)
        self.head = nn.Linear(embed_dim, num_classes)
    
    def forward(self, x):
        B = x.shape[0]
        x = self.patch_embed(x)                    # (B, 196, 768)
        
        cls_tokens = self.cls_token.expand(B, -1, -1)
        x = torch.cat([cls_tokens, x], dim=1)      # (B, 197, 768)
        x = x + self.pos_embed
        x = self.dropout(x)
        
        x = self.transformer(x)                     # (B, 197, 768)
        x = self.norm(x[:, 0])                      # CLS token → (B, 768)
        return self.head(x)                          # (B, num_classes)
```

## Positional Encoding

Unlike transformers for text, ViT typically uses **learnable positional embeddings** rather than sinusoidal encoding. The model learns to associate position information with each patch during training.

This is possible because ViT operates on fixed-size inputs — all images are the same resolution, so positional embeddings can be directly learned.

## Why ViT Needs More Data

CNNs have a built-in **inductive bias**: locality (small kernels look at local regions) and translation equivariance (same filter everywhere). ViT has neither — self-attention is global from the first layer.

| Architecture | Data Required | Why |
|-------------|---------------|-----|
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

```python
# Conceptual DINO training
teacher_output = teacher(global_crop)           # no gradient
student_output = student(local_crops)

teacher_output = teacher_output.detach()
# Apply centering and sharpening to teacher output
teacher_output = (teacher_output - center) / temperature
teacher_output = F.softmax(teacher_output, dim=-1)

loss = -(teacher_output * F.log_softmax(student_output / temperature)).sum(dim=-1).mean()
```

**Key finding**: DINO-trained ViT attention maps spontaneously learn semantic segmentation — attending to object boundaries without any labels. This suggests transformers learn meaningful visual representations through self-supervision.

## Hybrid CNN-Transformer Architectures

Combine CNN feature extraction with transformer reasoning:

| Model | CNN Stage | Transformer Stage | Benefit |
|-------|-----------|-------------------|---------|
| CoAT | Stem + MBConv | Transformer blocks | Gradual transition |
| CvT | Conv projection | Transformer | Reduced computation |
| Swin | Patch partition + CNN-like | Shifted window attention | Hierarchical features |

Hybrid models often outperform pure ViT on small datasets by leveraging CNN inductive biases early.

## ViT Variants

| Model | Layers | Embed Dim | Heads | Params | ImageNet Top-1 |
|-------|--------|-----------|-------|--------|----------------|
| ViT-B/16 | 12 | 768 | 12 | 86M | 84.2% |
| ViT-L/16 | 24 | 1024 | 16 | 307M | 85.2% |
| ViT-H/14 | 32 | 1280 | 16 | 632M | 88.6% |
| DeiT-S/16 | 12 | 384 | 6 | 22M | 81.8% (distilled) |

DeiT (Data-efficient Image Transformer) introduced distillation tokens to train ViT effectively on ImageNet alone.

## Key Takeaways

- ViT treats images as sequences of patches, applying standard transformer architecture
- Patch size determines resolution: smaller patches = more tokens = higher resolution but more computation
- ViT lacks CNN inductive biases (locality, translation equivariance), requiring more training data
- DINO shows self-supervised ViT learns semantically meaningful representations
- CLS token aggregation provides a single vector for classification tasks
- For limited data: use hybrid architectures or data-efficient training (DeiT)
- For large-scale: pure ViT scales better than CNNs with more data

## Common Bugs

| Bug | Symptom | Fix |
|-----|---------|-----|
| Wrong patch size / image size ratio | Positional embedding mismatch | Ensure `num_patches = (img_size // patch_size) ** 2` |
| Missing positional encoding | Random performance | Always add positional embeddings |
| Using ViT on tiny dataset | Severe overfitting | Use DeiT, hybrid model, or augment heavily |
| Not using CLS token output | Wrong prediction shape | Take `x[:, 0]` (CLS position) for classification |
| Forgetting to freeze CNN backbone (hybrid) | Memory overflow | Freeze early layers during fine-tuning |
| Wrong normalization for pretrained ViT | Poor accuracy | Use correct ImageNet normalization per variant |
