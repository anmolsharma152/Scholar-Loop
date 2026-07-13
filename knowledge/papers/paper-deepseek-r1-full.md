---
topic: papers
difficulty: hard
tags: [paper, reinforcement-learning, reasoning, chain-of-thought, distillation, open-source]
---

# DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning

## Problem & Motivation

- Existing LLMs rely on chain-of-thought (CoT) prompting for reasoning, but this requires careful prompting and doesn't work for all tasks
- Reinforcement learning (RL) has been used for alignment but not extensively for directly incentivizing reasoning
- Cold-start data can bootstrap reasoning capabilities but how to scale it remains unclear
- Distillation of reasoning abilities from large models to smaller ones is underexplored
- Reward hacking and language consistency during RL training are practical challenges

## Key Idea / Architecture

### DeepSeek-R1-Zero: Pure RL Reasoning
- Starts from base model (no SFT) and applies RL with rule-based reward
- Uses Group Relative Policy Optimization (GRPO) variant of PPO
- No labeled data — the model learns to reason purely from reward signals
- Demonstrates emergent behaviors: self-reflection, verification, long-chain reasoning

### DeepSeek-R1: Full Training Pipeline
1. **Cold Start**: Curate thousands of long CoT examples from DeepSeek-V3 (with some human annotation) for SFT
2. **Reasoning RL**: Apply GRPO on reasoning tasks using rule-based and process-based rewards
3. **Rejection Sampling**: Generate new data from RL checkpoint, mix with general SFT data
4. **Final RL**: Safety and helpfulness alignment with additional RL

### Key Techniques
- **GRPO (Group Relative Policy Optimization)**: Samples G outputs per prompt, normalizes rewards within group, eliminates value model
- **Rule-based Reward Model**: Avoids reward hacking from neural RMs
- **Language Consistency Reward**: Penalizes mixing languages during CoT
- **Temperature Rescaling**: Optimal temperature shifts from ~0.7 to ~1.2-1.3 during RL iterations

## Key Contributions

### 1. Pure RL Reasoning Emergence (R1-Zero)
- Without any SFT data, R1-Zero learns to reason through RL alone
- Performance on AIME 2024: starts near random, reaches 71.0% pass@1
- Emergent behaviors: self-verification ("Wait, let me check"), backtracking, error correction
- Reflective word frequency increases 5-7× during training

### 2. State-of-the-Art Reasoning Performance
| Benchmark | DeepSeek-R1 | OpenAI-o1-1217 | GPT-4o |
|-----------|-------------|-----------------|--------|
| AIME 2024 (Pass@1) | 79.8% | 79.2% | 9.3% |
| MATH-500 | 97.3% | 96.4% | 74.6% |
| Codeforces (Percentile) | 96.3% | 96.6% | 23.6% |
| GPQA Diamond | 71.5% | 75.7% | 49.9% |
| SWE Verified | 49.2% | 48.9% | 38.8% |

### 3. Effective Distillation to Smaller Models
- Distilled models (1.5B-70B) significantly outperform base models on reasoning
- DeepSeek-R1-Distill-Qwen-32B beats OpenAI-o1-mini on AIME 2024 (72.6% vs 63.6%)
- DeepSeek-R1-Distill-Llama-70B achieves 70.0% on AIME 2024

### 4. Analysis of Training Dynamics
- Accuracy by difficulty: level 1-3 problems plateau early (90-95%), level 4-5 continue improving
- Language consistency reward trades ~1% coding performance for readable output
- Reward hacking observed with neural RM — mitigated by rule-based rewards
- Total training cost: ~$294K on H800 GPUs (147K GPU hours)

### 5. Safety Evaluation
- Comparable safety to GPT-4o and Claude-3.5-Sonnet across 6 safety benchmarks
- Risk control system using DeepSeek-V3 as external reviewer
- HarmBench gap attributed to IP/copyright questions

## Results (Specific Numbers)

### Training Costs
- R1-Zero: 64×8 H800 GPUs for 198 hours (~$202K)
- R1: 64×8 H800 GPUs for 80 hours (~$82K)
- SFT data creation: 5K GPU hours (~$10K)
- Total: ~$294K

### Distillation Results
| Model | AIME 2024 | MATH-500 | GPQA Diamond |
|-------|-----------|----------|--------------|
| R1-Distill-Qwen-1.5B | 28.9% | 83.9% | 33.8% |
| R1-Distill-Qwen-7B | 55.5% | 92.8% | 49.1% |
| R1-Distill-Qwen-14B | 69.7% | 93.9% | 59.1% |
| R1-Distill-Qwen-32B | 72.6% | 94.3% | 54.5% |
| R1-Distill-Llama-8B | 50.4% | 89.1% | 49.0% |
| R1-Distill-Llama-70B | 70.0% | 94.5% | 57.5% |

### ChatbotArena Ranking
- R1 shares #1 position with OpenAI-o1 and Gemini-Exp-1206 (style control setting)
- #1 in math, #2 in coding on Arena leaderboard (as of Jan 24, 2025)

## Why It Matters / Impact

1. **Open-source reasoning**: MIT-licensed model competitive with proprietary frontier models
2. **RL for reasoning**: Demonstrates RL can directly incentivize reasoning without CoT prompting
3. **Distillation pipeline**: Practical method for transferring reasoning to smaller, deployable models
4. **Cost efficiency**: Entire R1 development costs <$300K — orders of magnitude less than comparable models
5. **Training dynamics insights**: Detailed analysis of emergent reasoning behaviors during RL

## Weaknesses / Limitations

1. **HarmBench gap**: Underperforms on copyright-related safety questions
2. **Language mixing**: Despite LC reward, some non-English tokens in CoT
3. **Engineering code**: Aider performance lower than OpenAI-o1 on software engineering tasks
4. **Reward hacking**: Neural reward models vulnerable to systematic exploitation
5. **N-gram contamination**: Cannot prevent paraphrased benchmark contamination
6. **Temperature sensitivity**: Optimal hyperparameters shift during training

## Follow-up Work

- Extending reasoning to more domains (not just math/code)
- Improving engineering task performance with more SWE data
- Better language consistency methods beyond reward penalties
- Investigating emergent reasoning behaviors at even larger scales
- Combining process-based and outcome-based rewards more effectively
