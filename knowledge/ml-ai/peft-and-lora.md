---
difficulty: medium
last_sent: null
review_count: 0
tags:
- peft
- lora
- fine-tuning
topic: ml-ai
---

# PEFT and LoRA

Full fine-tuning of large language models is prohibitively expensive — updating all parameters of a 7B model requires ~28GB of GPU memory just for the weights (in FP32), plus gradients and optimizer states. Parameter-Efficient Fine-Tuning (PEFT) techniques freeze most of the model and only train a small number of new or selected parameters, achieving comparable performance at a fraction of the cost.

## Why Full Fine-Tuning Is Expensive

For a model with `Φ` parameters, full fine-tuning requires storing:

- **Model weights**: Φ parameters
- **Gradients**: Φ parameters
- **Optimizer states** (Adam): 2Φ parameters (momentum + variance)
- **Total**: ~4Φ parameters in memory

For a 7B parameter model at FP32: ~112 GB of GPU memory just for optimizer states. This makes fine-tuning inaccessible without multi-GPU setups. Even at FP16, a 7B model needs ~14 GB just for weights.

The key insight of PEFT: most of the information needed for a new task is already captured in the pre-trained weights. Only a small "delta" needs to be learned.

## LoRA (Low-Rank Adaptation)

LoRA (Hu et al., 2021) is the most popular PEFT method. Instead of updating a weight matrix W of shape `(d, k)`, LoRA decomposes the update as:

```
W' = W + ΔW = W + BA
```

Where:
- B has shape `(d, r)` and A has shape `(r, k)`
- `r << min(d, k)` — the rank (typically 4-64)
- Only B and A are trained; W is frozen

This reduces trainable parameters from `d × k` to `d × r + r × k`. For a typical attention projection (4096 × 4096) with r=8: from 16.7M to 65K parameters — a **256x reduction**.

```python
import torch
import torch.nn as nn

class LoRALinear(nn.Module):
    def __init__(self, original_linear, rank=8, alpha=16):
        super().__init__()
        self.original = original_linear
        self.original.weight.requires_grad = False  # freeze base weights

        d_out, d_in = original_linear.weight.shape
        self.lora_A = nn.Parameter(torch.randn(d_in, rank) * 0.01)
        self.lora_B = nn.Parameter(torch.zeros(rank, d_out))
        self.scaling = alpha / rank

    def forward(self, x):
        # Base output + low-rank delta
        base_output = self.original(x)
        lora_output = (x @ self.lora_A @ self.lora_B) * self.scaling
        return base_output + lora_output
```

The `alpha` parameter controls the magnitude of the LoRA update. `scaling = alpha / rank` means increasing alpha amplifies the adaptation without changing the rank. Common practice: set alpha = 2 × rank.

## Applying LoRA to a Model

LoRA is typically applied to attention projection layers (Q, K, V, and output projections). It can also be applied to FFN layers for better performance.

```python
from peft import get_peft_model, LoraConfig, TaskType

def apply_lora(model, rank=8, target_modules=["q_proj", "v_proj"]):
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=rank,
        lora_alpha=16,
        lora_dropout=0.05,
        target_modules=target_modules,
    )
    peft_model = get_peft_model(model, lora_config)
    peft_model.print_trainable_parameters()
    # Output: trainable params: 4,194,304 || all params: 6,742,609,920 || trainable%: 0.06%
    return peft_model
```

At inference, LoRA weights can be **merged** into the base model (`W' = W + BA`), adding zero latency overhead.

## Other PEFT Methods

| Method | Approach | Trainable Params | Notes |
|--------|----------|-----------------|-------|
| **LoRA** | Low-rank weight updates | ~0.1-1% | Most popular, mergeable |
| **QLoRA** | LoRA on quantized (4-bit) base | ~0.1-1% | Fits 7B on single GPU |
| **Adapter** | Insert small bottleneck layers | ~1-5% | Adds inference latency |
| **Prompt tuning** | Learn soft prompt embeddings | <0.01% | Very lightweight |
| **Prefix tuning** | Prepend learned key/value prefixes | ~0.1% | Similar to prompt tuning |
| **IA3** | Learn rescaling vectors | <0.01% | Extremely parameter-efficient |
| **BitFit** | Only train bias terms | ~0.1% | Surprisingly effective |

## Adapter Layers

Adapters (Houlsby et al., 2019) insert small bottleneck layers after each Transformer sub-layer:

```
x → LayerNorm → Down-project (d → r) → Activation → Up-project (r → d) → + x (residual)
```

The down-projection reduces dimensionality, the activation introduces non-linearity, and the up-projection restores the original dimension. Only the adapter parameters are trained; the rest of the model is frozen.

Unlike LoRA, adapters add inference latency (extra layers to compute). LoRA's mergeable nature gives it an edge for deployment.

## Prompt Tuning and Prefix Tuning

These methods add **learnable continuous vectors** to the input:

- **Prompt tuning**: Prepend `n` learned "soft tokens" to the input embeddings. Only these tokens are trained. At scale (10B+ params), prompt tuning matches fine-tuning.
- **Prefix tuning**: Similar idea, but learned vectors are prepended to K and V in every attention layer, giving more control over the model's internal representations.

```python
class PromptTuning(nn.Module):
    def __init__(self, num_virtual_tokens, d_model):
        super().__init__()
        self.soft_prompts = nn.Parameter(torch.randn(num_virtual_tokens, d_model) * 0.01)

    def forward(self, input_embeddings):
        batch = input_embeddings.size(0)
        prompts = self.soft_prompts.unsqueeze(0).expand(batch, -1, -1)
        return torch.cat([prompts, input_embeddings], dim=1)
```

## QLoRA

QLoRA (Dettmers et al., 2023) combines 4-bit quantization with LoRA:

1. Quantize the base model to 4-bit NF4 (NormalFloat4) with double quantization
2. Add LoRA adapters in FP16/BF16 on top of the quantized model
3. Train only the LoRA parameters

This enables fine-tuning a 7B model on a single 24GB GPU (or even 16GB), democratizing LLM fine-tuning.

## Key takeaways

- LoRA is the default choice for most fine-tuning tasks — effective, fast, and mergeable
- The rank parameter (r) controls the capacity-performance tradeoff: r=8 is a good default, r=32-64 for complex tasks
- Merge LoRA weights into the base model after training for zero-inference-overhead deployment
- QLoRA makes 7B-13B models fine-tunable on consumer GPUs
- PEFT methods can be combined: LoRA + prompt tuning, etc.

## Common bugs

- Forgetting to set `requires_grad = False` on the base model — accidentally fine-tuning everything defeats the purpose
- Using LoRA on all layers when only attention is needed — wastes parameters with diminishing returns
- Not using `peft_model.merge_and_unload()` before deployment — leaves LoRA as separate computation
- Choosing rank too high (r=256+) — approaches full fine-tuning cost, losing the PEFT advantage
- Forgetting to set `r` and `alpha` consistently across experiments — makes results incomparable
- Applying LoRA to embedding layers without checking task compatibility — often hurts more than helps
