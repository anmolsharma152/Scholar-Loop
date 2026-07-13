---
topic: papers
difficulty: hard
last_sent:
review_count: 0
tags:
  - paper
  - mixture-of-experts
  - large-scale
  - distributed-training
  - transformers
---

# GShard: Scaling Giant Models with Conditional Computation and Automatic Sharding

**Authors:** Dmitry Lepikhin, HyoukJoong Lee, Yuanzhong Xu, Dehao Chen, Orhan Firat, Yanping Huang, Maxim Krikun, Shixia Shao, Zeqiang Huang, Yuanzhong Xu, Daihyun Kim, Lukasz Kaiser, Barret Zoph, Qifeng V. Le, Zhifeng Chen (Google)
**Published:** International Conference on Learning Representations (ICLR) 2021
**arXiv:** 2006.16668

## Problem & Motivation

Training giant neural networks requires enormous compute and memory resources that exceed single-device capacity. Prior work on model parallelism either partitioned layers vertically (across depth) or horizontally (across width), but neither approach was scalable to hundreds of devices with billions of parameters. Mixture-of-Experts (MoE) models can scale model capacity cheaply by conditioning computation on each input, but efficient parallelization of MoE across 2000+ devices was unsolved. The challenge was to enable training of 600B-parameter models on 2048 TPU v3 chips in 4 days while maintaining model quality.

## Key Idea / Architecture

GShard introduces a framework that automatically shards models across devices using a combination of data, model, and expert parallelism, controlled by simple annotations.

**Conditional computation via MoE:** Every other Transformer layer is replaced with an MoE layer using top-2 gating. The gating network is a linear transformer per expert, producing probability P_i(x) for token x. The top-2 experts are selected, with the final representation being a weighted combination of both experts' outputs. This top-2 approach provides redundancy—when one expert is overloaded, the second expert's contribution provides a quality safety net.

**Automatic sharding rules:** Users annotate tensor dimensions with sharding specifications (e.g., "data-parallel", "model-parallel", "expert-parallel"). The XLA compiler partitions tensors accordingly and inserts communication primitives (all-reduce, all-to-all) automatically. This replaces manual partitioning logic with a declarative specification.

**3D parallelism:** Data parallelism replicates the model across batches, model parallelism partitions tensors within layers, and expert parallelism places different experts on different devices. All-to-all collective communication dispatches tokens to the appropriate experts across devices.

**Balanced constraints:** To prevent device imbalance, GShard uses a capacity factor: each expert can process at most CF × (total_tokens / num_experts) tokens, with CF=1.5. Overflowed tokens are dropped (in practice, negligible at <1% with CF=1.5). The auxiliary load balancing loss from Shazeer et al. (2017) is used to encourage uniform expert utilization.

**Token routing improvements:** Each input token is dispatched to exactly the top-2 experts, and outputs are combined with softmax-weighted combinations. A random routing policy with probability f is added to the top-2 selection (f=0.01) to maintain exploration.

## Key Contributions

1. Automatic parallelization framework with declarative sharding annotations, reducing implementation effort for distributed training.
2. Top-2 MoE routing with capacity factors to balance load across 2048 devices, handling up to 600B parameters.
3. Scaling demonstration: 600B parameters trained on 2048 TPU v3 in 4 days on 100-to-1 translation.
4. Conditional computation paradigm: MoE layers activate only ~10B parameters per token despite 600B total, providing 60× compute savings vs. dense.

## Results (Specific Numbers)

- 600B parameter model (≈600× T5-XXL) trained in 4 days on 2048 TPU v3
- Only ~10B parameters active per token (1.7% activation)
- WMT'14 En-De BLEU: 29.3 (vs. 29.1 for previous SOTA); En-Ru BLEU: 34.4 (vs. 34.3)
- Machine translation: GShard achieves SOTA across all 100 languages tested
- Automatic parallelization: achieves 3× speedup vs. hand-tuned parallelism in comparable settings
- Capacity factor 1.5 balances quality and load; CF=1.2 degrades quality by ~1 BLEU due to dropped tokens
- Top-2 routing outperforms top-1 by 0.3–0.5 BLEU on translation tasks
- Training is stable across 4 days of continuous operation on 2048 chips
- 100-to-1 translation (En-→100 languages): GShard outperforms baseline on 87/100 languages, matching on remaining 13
- Sharding annotation overhead: ~30 additional lines of code vs. non-sharded baseline (negligible development cost)
- Top-2 routing with random exploration (f=0.01): 0.2 BLEU improvement over top-2 alone
- Scaling from 2B to 600B: translation quality improves 1.8 BLEU average across 100 languages
- Expert utilization: average 89% of experts active per batch (vs. ~10% for top-1 routing without balancing)
- All-to-all communication overhead: ~12% of total training time at 2048 devices, negligible at 512 devices

## Why It Matters / Impact

GShard demonstrated that trillion-scale models were trainable on existing hardware with careful parallelization. The framework's declarative sharding approach influenced later systems like Megatron-LM, DeepSpeed, and JAX's automatic sharding. The top-2 routing and capacity factor designs became standard in MoE implementations. GShard's success on multilingual translation showed that massive conditional computation could improve quality across diverse tasks simultaneously.

## Weaknesses / Limitations

1. The automatic sharding framework still requires careful specification of sharding dimensions; incorrect annotations can lead to subtle bugs or poor performance.
2. Token dropping at capacity factor boundaries introduces noise; while typically <1%, this can be problematic for long-tail or imbalanced datasets.
3. Top-2 routing approximately doubles per-token computation compared to top-1, though total activated parameters are still much smaller than dense models.
4. Communication overhead from all-to-all expert dispatch scales with the number of devices, creating a practical upper bound on expert count.
5. The study focuses on translation and does not evaluate on diverse NLP benchmarks or general language modeling.

## Follow-up Work

- Switch Transformers (Fedus et al., 2021): Replaced top-2 with top-1 routing for further efficiency gains.
- ST-MoE (Zoph et al., 2022): Stable MoE training techniques building on GShard's infrastructure.
- PaLM and PaLM-2: Production LLMs leveraging MoE at scale based on lessons from GShard.
- Open-source implementations: Fairseq and Mesh-TensorFlow adopted GShard's sharding paradigm.
- Universal Transformer (Dehghani et al., 2018): Dynamic computation that GShard scales to trillion parameters.
- mT5: Multilingual T5 using GShard-style expert parallelism for training on C4-101 languages.
