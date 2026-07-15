---
topic: ml-ai
difficulty: medium
tags: [finetuning, peft, prompt-tuning, prefix-tuning]
last_sent:
review_count: 0
---

# PEFT: Prompt Tuning & Prefix Tuning

## Prompt Tuning
Instead of modifying model weights, add learnable "soft prompt" tokens to the input embedding layer.

**How it works:** Learn k virtual tokens each of dimension d (same as word embeddings). These are prepended to the input embedding sequence and optimized via gradient descent. For k virtual tokens, that's k×d new parameters (e.g., k=20, d=4096 → 82K parameters for Llama 2 7B).

**Comparison with prompt engineering:**
- Hard prompts (hand-written): "Translate French to English: ..."
- Soft prompts (learned): [v1, v2, ..., vk] + "Translate French to English: ..."

**Performance:** Soft prompts contain ~0.01% of model parameters but approach full fine-tuning performance on many NLP tasks. Works best when the soft prompt length matches the complexity of the task.

## Prefix Tuning
Insert learnable vectors into every Transformer layer's key/value heads, not just the input embedding.

**Mechanism:** For each Transformer layer i, maintain two matrices P_i^k ∈ ℝ^{l×d_k} and P_i^v ∈ ℝ^{l×d_v} where l is prefix length. These are concatenated with the actual key and value sequences during attention computation: K' = [P_i^k; K], V' = [P_i^v; V]. The prefix tokens participate in attention but don't have corresponding hidden states.

**Reparameterization:** Prefix vectors are not optimized directly in parameter space but through a bottleneck MLP: P_i^v = MLP_θ(P_i'^v) where P_i'^v ∈ ℝ^{l×d_mid} and d_mid ≪ d. After training, the MLP is discarded and the final prefix vectors are used directly.

**Size:** About 0.1-2% of full model parameters. For GPT-2 Medium (355M): 0.25M prefix parameters (0.07% full size).

## Comparison Table

| Method | Parameter Count | Performance | Speed |
|---|---|---|---|
| Full Fine-tuning | 100% | Baseline | Slowest |
| LoRA | 0.01-0.5% | 95-99% of FT | Near full inference |
| Adapters | 1-5% | 96-99% of FT | 5-10% slower inference |
| Prompt Tuning | ~0.01% | 80-95% of FT | Full inference speed |
| Prefix Tuning | 0.1-2% | 95-99% of FT | Full inference speed (reparameterized) |

## Practical Guidance

**Choose LoRA when:** Task-specific quality is critical, you have labeled data, or you need multiple task-specific models.

**Choose Prompt Tuning when:** Models are very large (>100B), model access is API-only, or rapid task switching is needed.

**Adapters:** Useful when you need more capacity than LoRA but don't want full fine-tuning. Historical significance but largely supplanted by LoRA.

**Combining methods:** LoRA + Prefix Tuning can be complementary. Each captures different aspects of task adaptation.
