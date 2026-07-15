---
difficulty: hard
tags: [cv, vit, transformer]
topic: ml-ai
last_sent:
review_count: 0
---

# Vision Transformers: Architecture

ViT (Dosovitskiy et al., 2020) applies the transformer architecture directly to images, replacing convolutional layers entirely. It treats an image as a sequence of patches:

1. **Split image into patches:** Reshape image of size (H, W, C) into N = (H·W)/P² patches of size (P·P·C)
2. **Linear projection:** Map each patch to a D-dimensional embedding
3. **Add positional encoding:** Inject spatial information (patches have no inherent order)
4. **Prepend CLS token:** Learnable token whose final representation is used for classification
5. **Pass through transformer encoder:** Standard self-attention + FFN blocks
6. **Classify from CLS token:** Use final CLS embedding for prediction

## Code Implementation

```python
class PatchEmbedding(nn.Module):
    def __init__(self, img_size=224, patch_size=16, in_channels=3, embed_dim=768):
        super().__init__()
        self.num_patches = (img_size // patch_size) ** 2
        self.proj = nn.Conv2d(in_channels, embed_dim,
                              kernel_size=patch_size, stride=patch_size)
    def forward(self, x):
        x = self.proj(x)
        x = x.flatten(2).transpose(1, 2)
        return x
```

Key implementation details: the patch embedding is implemented as a strided convolution (efficient), and the CLS token is concatenated to the patch sequence before the positional embedding is added.

## Positional Encoding

ViT uses **learnable positional embeddings** rather than sinusoidal encoding. This works because ViT operates on fixed-size inputs — all images are the same resolution so position embeddings are consistent. The model learns to associate position information with each patch during training.

## Common Bugs

| Bug | Symptom | Fix |
|-----|---------|-----|
| Wrong patch size / image size ratio | Positional embedding mismatch | Ensure `num_patches = (img_size // patch_size) ** 2` |
| Missing positional encoding | Random performance | Always add positional embeddings |
| Not using CLS token output | Wrong prediction shape | Take `x[:, 0]` for classification |
| Wrong normalization for pretrained ViT | Poor accuracy | Use correct ImageNet normalization per variant |
