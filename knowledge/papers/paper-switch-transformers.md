---
topic: papers
difficulty: hard
last_sent:
review_count: 0
tags:
  - paper
  - mixture-of-experts
  - sparsity
  - scaling
  - transformers
---

# Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity

**Authors:** William Fedus, Barret Zoph, Noam Shazeer (Google Brain)
**Published:** Journal of Machine Learning Research 23 (2022)
**arXiv:** 2101.03961

## Problem & Motivation

Scaling language models improves performance but increases computational cost, communication bandwidth, and memory requirements proportionally. Dense models must activate all parameters for every token, creating a fundamental tension between model capacity and per-token compute. Mixture-of-Experts (MoE) offers a solution by activating only a subset of parameters per input token, but prior MoE implementations (Shazeer et al., 2017) were complex, brittle, required large batch sizes for efficiency, and used top-2 gating that doubled per-token compute compared to sparse alternatives.

## Key Idea / Architecture

Switch Transformers uses **top-1 routing**: each token is routed to exactly one expert (out of N experts), making the model sparse at the token level while each individual expert remains dense. The router is a simple linear layer with softmax normalization, selecting the expert with highest probability for each token.

The auxiliary load balancing loss encourages uniform expert assignment. For each token i routed to expert j, define binary indicator f(i,j)=1 if token i is assigned expert j. The loss is:

L_aux = α · N · Σ_i (f_i · p_i)

where p_i is the router probability vector and α is a small coefficient (default 0.01). This penalizes imbalanced usage without requiring a perfect uniform distribution.

**Expert architecture:** Each expert is a feedforward network identical to the base model's dense FFN but with potentially different widths. The model replaces every other Transformer FFN layer with a Switch layer (alternating dense and MoE layers). With 128 experts, this creates 2048 experts across all layers. Total capacity reaches 1.6 trillion parameters with only 100B activated per token.

**Precision and efficiency improvements:**
1. Selective precision: Compute gating in float32 for training stability, but expert computation in bfloat16 for 2× speedup.
2. Importance gating: Route tokens to experts within the same mesh processor when possible, reducing communication.
3. Small expert FFNs: Use n/experts hidden dimension per expert (instead of full n), keeping computation roughly constant per expert as N grows.

**Model variants:** Switch-Base (≈74M params), Switch-Large (≈1.5B), Switch-XL (≈1.6T). Switch-XL uses 2048 experts across 128 TPU v3 chips in a 2D mesh topology.

## Key Contributions

1. Simplified MoE routing with top-1 gating, reducing computation by 50% vs. top-2 while matching or exceeding quality.
2. Auxiliary load balancing loss (α=0.01) that is simpler and more effective than capacity-based penalties.
3. Scaling demonstration to 1.6 trillion parameters—600× larger than the largest existing dense model at the time.
4. 7× pre-training speedup vs. dense T5-XXL on comparable compute budgets while using same parameters.
5. 4× speedup in fine-tuning vs. dense models, with similar or better downstream task performance.

## Results (Specific Numbers)

- Pre-training: Switch-XXL (≈68B parameters) matches T5-XXL (≈11B) quality at 4× less compute, reaching same perplexity in 2.25 steps vs. 9 for T5-XXL
- 7× speedup of Switch-XL vs. T5-XXL on the same compute budget
- 1.8× speedup of Switch-Base vs. T5-Base during fine-tuning
- Fine-tuning Switch-Base reaches T5-Base quality at 2.25× faster; Switch-XL reaches T5-XXL at 1.46× faster
- MNLI accuracy: Switch-Base 92.0 vs. T5-Base 90.2; Switch-Large 94.2 vs. T5-Large 92.3
- SQuAD: Switch-Large 95.4 vs. T5-Large 94.1
- GLUE average: Switch-Large 88.7 vs. T5-Large 86.7
- 128 experts (best quality-speed tradeoff): 1.4× speedup over 2-expert model
- α=0.01: best balance of quality and load balancing; α>0.01 hurts performance
- 2D mesh on 128 TPU v3: 4× faster than 1D model parallelism
- Unstructured sparse dense model (64.1% sparsity): 1.6× faster than dense T5-Base

## Why It Matters / Impact

Switch Transformers demonstrated that MoE sparsity could be scaled to trillion-parameter models with simple, efficient routing. This approach underpins Google's PaLM-2 and Mixtral models. The paper established practical guidance for MoE hyperparameters (α=0.01, top-1 routing, expert capacity scaling) that became widely adopted. The 7× pre-training speedup fundamentally changed the compute-performance tradeoff landscape.

## Weaknesses / Limitations

1. All-experts-active evaluation: For fair comparison with dense models, inference requires running all experts per token, negating the sparsity advantage at inference time.
2. Load balancing is imperfect: The auxiliary loss creates tension between routing quality and uniform usage, leading to suboptimal expert assignments.
3. Expert specialization is limited: Analysis shows experts do specialize on syntactic/semantic features but the degree varies unpredictably across layers.
4. Distributed training complexity: 128 TPU v3 chips required; communication overhead grows with expert count and model dimension.
5. The model underperforms at very large batch sizes during fine-tuning (quality degrades above 2^20 tokens/batch), limiting some use cases.

## Follow-up Work

- GShard (same authors, 2020): Preceding work demonstrating MoE at 600B scale with top-2 routing.
- Mixtral 8x7B: Community adoption of top-2 MoE with strong open-source results.
- PaLM-2: Google's production LLMs using Switch-style MoE.
- DeepSeek-MoE: Fine-grained expert segmentation achieving better quality per parameter.
