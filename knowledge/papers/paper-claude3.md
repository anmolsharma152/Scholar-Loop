---
difficulty: hard
last_sent: 2026-07-13 23:30:14.588682+00:00
review_count: 1
tags:
- paper
- claude
- constitutional-ai
- safety
- multimodal
- alignment
topic: papers
---

# The Claude 3 Model Family: Opus, Sonnet, Haiku

**Authors:** Anthropic
**Published:** Anthropic Technical Report, March 2024
**arXiv:** N/A - not on arXiv

## Problem & Motivation

Frontier LLMs need to balance capability, speed, and cost across different deployment scenarios while maintaining strong safety guarantees. Long-context retrieval beyond 100K tokens requires near-perfect recall without degradation. Safety evaluations for catastrophic risks (biological, cyber, autonomous replication) are critical but underdeveloped at the industry level. The Claude 3 family aims to set new benchmarks across reasoning, math, coding, multilingual understanding, and vision while being deployable through consumer APIs (Claude.ai, Claude Pro) and enterprise platforms (Anthropic API, Amazon Bedrock, Google Vertex AI).

## Key Idea / Architecture

### Model Family Design

Claude 3 is a family of three models: Opus (most capable), Sonnet (balanced speed and capability), and Haiku (fastest and least expensive). All models are multimodal with native vision capabilities for image input (JPEG/PNG/GIF/WebP, up to 10MB and 8000x8000px) alongside text. The context window extends up to 200K tokens. Knowledge cutoff is August 2023.

### Training Methodology

Training uses Constitutional AI (CAI) combined with RLHF. Models are given a constitution of ethical and behavioral principles sourced from the UN Declaration of Human Rights, trained to avoid sexist, racist, and toxic outputs. A new principle from Collective Constitutional AI instructs Claude to be accessible to individuals with disabilities, reducing stereotype bias. Training was done on AWS and Google Cloud with PyTorch, JAX, and Triton frameworks. Data includes publicly available internet data as of August 2023 plus licensed third-party data, with deduplication and classification filtering.

### Responsible Scaling Policy (RSP)

All Claude 3 models classified at ASL-2 (lowest risk tier). Risk categories include Biological, Cyber, and Autonomous Replication & Adaptation (ARA). Pre-specified warning thresholds trigger higher safety requirements. Evaluations include human red-teaming, automated classifiers, and human uplift trials for biological risk.

## Key Contributions

1. Three-tier model family with linear scaling of cost vs capability: Opus MMLU 86.8%, Sonnet 79.0%, Haiku 75.2%
2. Near-perfect long-context recall: 99.4% average across all context lengths, 98.3% at 200K tokens on Needle in a Haystack
3. First detailed public Responsible Scaling Policy framework with structured risk evaluations for ARA, biological, and cyber threats
4. Comprehensive multimodal safety testing: 378 prompts, Opus 97.9% harmless, Sonnet 99.2% harmless

## Results (Specific Numbers)

### Core Benchmarks

| Benchmark | Opus | Sonnet | Haiku | GPT-4 |
|-----------|------|--------|-------|-------|
| MMLU (5-shot) | 86.8% | 79.0% | 75.2% | 86.4% |
| GPQA Diamond (0-shot CoT) | 50.4% | 40.4% | 33.3% | — |
| MATH (4-shot) | 61% | 40.5% | 40.9% | 52.9% |
| GSM8K (Maj1@32) | 95.0% | 92.3% | 88.9% | 92.0% |
| HumanEval (0-shot) | 84.9% | 73.0% | 75.9% | 67.0% |
| QuALITY (1-shot) | 90.5% | 85.9% | 80.2% | — |

### GPQA Diamond Maj@32 (5-shot CoT)

- Opus: 59.5%, Sonnet: 46.3% (averaged over 10 evaluation rollouts due to high variance)

### Safety Evaluations

- ARA: Failed 3 or more of 5 catastrophic tasks (Flask exploit, LLM backdoor, SQL injection, API copycat, LM worm) — not at ASL-3 threshold
- Biological: No ASL-3 threshold crossed; human uplift trials showed minor accuracy improvement with model access
- Cyber: 30% on one vulnerability discovery task (required substantial hints; not at ASL-3 threshold)
- Multimodal: 378 red-team prompts, Opus 370/378 harmless (97.9%), Sonnet 375/378 (99.2%)

### Bias and Discrimination

- BBQ (Bias Benchmark for QA): Opus achieves highest accuracy in disambiguated context and lowest bias in ambiguous context across 10 demographic characteristics

## Why It Matters / Impact

Claude 3 established the tiered model family paradigm (Opus/Sonnet/Haiku) now standard across the industry. The Responsible Scaling Policy provided a concrete, auditable methodology for safe frontier model deployment that influenced how other labs approach safety governance. Near-perfect 200K token recall enabled practical long-document applications without complex RAG pipelines. The model family also improved fluency in non-English languages including Spanish and Japanese.

## Weaknesses / Limitations

- Knowledge cutoff August 2023 with no native web search capability
- Multimodal failures include hallucinated image descriptions and missed harmful content in images
- Low-resource language performance is less robust
- Safety tuning can produce over-refusal of legitimate prompts
- ARA evaluations may not fully capture autonomous replication potential
- Western demographic skew in pretraining data
- 200K context available but 1M context not yet deployed at time of report

## Follow-up Work / Key References

- Anthropic's Claude 3.5 Sonnet and Opus updates (2024) — improved performance and efficiency
- Extended to 1M+ token production contexts in later Claude versions
- Constitutional AI (Bai et al., 2022) — foundational alignment methodology for Claude
- Red Teaming Language Models to Reduce Harms (Perez et al., 2022) — safety evaluation approach
- Collective Constitutional AI (2023) — public input process for constitution principles