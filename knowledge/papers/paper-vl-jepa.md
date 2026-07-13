---
topic: papers
difficulty: hard
tags: [paper, vision-language, self-supervised, joint-embedding, multimodal, representation-learning]
last_sent:
review_count: 0
---

# VL-JEPA: Towards Unified Vision-Language Learning via Joint Embedding Predictive Architecture

## Problem & Motivation
Current vision-language models typically rely on contrastive objectives (like CLIP) that require large batches of negative samples and alignment between modalities in pixel/text space. These approaches are computationally expensive and may not capture the most semantically meaningful shared representations. The goal was to extend the JEPA framework to the vision-language domain, learning aligned representations without pixel-level prediction or contrastive losses.

## Key Idea / Architecture
VL-JEPA extends the JEPA architecture to handle both video and text:
1. **Video encoder**: Processes video frames using a ViT-based architecture
2. **Text encoder**: Processes language descriptions using a text transformer
3. **Cross-modal prediction**: The model predicts masked representations in one modality from visible representations in both modalities
4. **Joint embedding space**: Video and text share a common representation space trained via JEPA objectives
5. **Selective decoding**: A key innovation where only the most relevant parts of the representation are decoded, achieving ~2.85x reduction in decoding computation

The model uses attention-based masking where the model learns which parts of the input to attend to, rather than using fixed masking patterns.

## Key Contributions
- Extended JEPA to the vision-language domain
- Selective decoding reduces computation by ~2.85x while maintaining performance
- 50% fewer parameters than comparable vision-language models
- No contrastive loss needed: JEPA objective provides sufficient learning signal
- Unified architecture handles both video understanding and language tasks
- Strong performance on video question answering and retrieval benchmarks

## Results
- **Parameter efficiency**: 50% fewer parameters than comparable VL models while maintaining performance
- **Selective decoding**: 2.85x reduction in decoding FLOPs with minimal quality loss
- **Video QA**: Competitive with state-of-the-art on video question answering benchmarks
- **Retrieval**: Strong performance on video-text retrieval tasks
- **Unified architecture**: Single model handles both video and language understanding
- **Training efficiency**: JEPA objective is more efficient than contrastive learning (no negative sampling)

## Why It Matters / Impact
VL-JEPA demonstrates that the JEPA framework can be extended to multimodal settings without the computational overhead of contrastive learning. The selective decoding innovation is particularly significant—it shows that not all representation dimensions are equally important for downstream tasks, and selectively decoding the most relevant dimensions can dramatically reduce computation. This has implications for deploying vision-language models on resource-constrained devices. The work also establishes that unimodal JEPA principles (predict in representation space) transfer effectively to cross-modal learning.

## Weaknesses / Limitations
- Evaluation limited to video-language tasks; image-language tasks not explored
- The selective decoding mechanism adds architectural complexity
- No analysis of what information is discarded by selective decoding
- Performance may degrade on tasks requiring fine-grained visual details
- The model requires careful hyperparameter tuning for the cross-modal masking
- Limited comparison with the latest vision-language models (e.g., Flamingo, GPT-4V)
