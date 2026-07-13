---
topic: papers
difficulty: hard
last_sent:
review_count: 0
tags:
  - paper
  - multi-agent
  - orchestration
  - evolutionary
  - sakana
---

# Sakana Fugu Technical Report

**Authors:** Fugu Team (Sakana AI)
**Published:** arXiv June 2026
**arXiv:** 2606.21228

## Problem & Motivation

Frontier LLMs increasingly specialize in distinct domains—GPT-series excels at math reasoning, Opus-series at software engineering and cybersecurity, Gemini at direct algorithm implementation. No single model dominates across all tasks. The authors asked whether a trained orchestrator could combine these complementary specializations into a collectively intelligent system that surpasses any individual model. Traditional multi-agent approaches rely on hand-designed workflows, but learned orchestration could dynamically route queries to the most capable agent for each input. If capability can be scaled through orchestration, progress need not depend solely on the largest training runs. The growing ecosystem of diverse frontier models creates an opportunity for collective intelligence.

## Key Idea / Architecture

Sakana Fugu is a family of orchestrator language models that coordinate a pool of frontier LLM workers (including Gemini-3.1-Pro, Claude-Opus-4.8, and GPT-5.5). The system exposes a single model interface to users while internally routing, delegating, and coordinating across multiple specialized agents.

Fugu (the latency-optimized variant) uses a lightweight prediction head attached to the orchestrator's final hidden layer. Given hidden state h in R^d, the head outputs L logits scoring which worker model should handle the input. A small subset of backbone parameters are adapted using singular-value fine-tuning (only singular-value scales are trained, orthogonal components fixed). Training proceeds in two stages: (1) supervised fine-tuning on single-step verifiable tasks using soft performance distributions over workers as targets (KL divergence loss), and (2) evolutionary optimization using sep-CMA-ES to maximize terminal reward on end-to-end agentic trajectories from coding environments.

Fugu-Ultra (the performance-optimized variant) builds on the Conductor framework, using GRPO reinforcement learning to train a language model that designs full agentic workflows—specifying subtasks, worker assignments, and communication topologies for up to 5 steps. It handles multi-agent function calling through intra-workflow agent isolation (preventing orchestration collapse) and persistent shared memory across workflows.

```
Fugu selection: a_t ~ pi_theta(.|s_t), where pi_theta(a|s) proportional to exp(f_theta(h(s))_a)
Fugu-Ultra reward: r_i = 1 if workflow output matches solution, 0.5 otherwise
```

## Key Contributions

1. Demonstrated that trained orchestration of existing frontier models can surpass the best individual models across coding, reasoning, and scientific benchmarks
2. Introduced a two-stage training paradigm combining supervised fine-tuning on soft rankings with evolutionary optimization on end-to-end trajectories
3. Achieved SOTA on SWE Bench Pro (73.7%) and Terminal Bench 2.1 (82.1%) through multi-agent coordination
4. Showed that learned orchestration constitutes a new scaling axis beyond ever-larger individual models
5. Open-sourced the models, enabling frontier-level capability without proprietary API access
6. Fugu-Ultra handles multi-agent function calling through intra-workflow isolation and persistent shared memory across workflows

## Results (Specific Numbers)

- SWE Bench Pro: Fugu-Ultra 73.7% (vs. Claude Opus 4.8 69.2%, GPT-5.5 58.6%)
- Terminal Bench 2.1: Fugu-Ultra 82.1% (vs. Claude Opus 4.8 74.6%, GPT-5.5 60.1%)
- GPQA Diamond: Fugu 95.5% (tied with Claude Opus 4.8, vs. GPT-5.5 93.6%)
- Humanity's Last Exam: Fugu-Ultra 50.0% (vs. Claude Opus 4.8 49.8%, GPT-5.5 41.4%)
- LiveCodeBench v6: Fugu-Ultra 92.0% (vs. GPT-5.5 90.7%)
- CharXiv Reasoning: Fugu-Ultra 86.6% (vs. Claude Opus 4.8 84.2%)
- tau3 Banking: Fugu-Ultra 20.6% (vs. Claude Opus 4.8 20.6%)
- SciCode: Fugu-Ultra 58.7% (vs. Claude Opus 4.8 53.5%)

## Why It Matters / Impact

Sakana Fugu demonstrates that intelligence can be amplified by composing existing models rather than only training larger ones. If capability can be scaled through orchestration, progress need not depend solely on the largest training runs. This makes frontier capability more modular, accessible, and configurable—users can restrict agent pools to specific providers for compliance. The approach also suggests economic and geopolitical implications, distributing frontier AI benefits more broadly rather than concentrating them in those able to train the largest models. The finding that a lightweight orchestrator can surpass its most capable worker suggests that the collective intelligence of a model team exceeds any individual member. This challenges the prevailing assumption that bigger individual models are always better.

## Weaknesses / Limitations

- Depends on availability of frontier models in the worker pool; performance degrades if pool members are weaker or unavailable
- Latency overhead from orchestration, even in the optimized Fugu variant—each query requires an additional forward pass through the orchestrator
- Training requires access to many different frontier models and their APIs, creating significant infrastructure complexity and ongoing cost
- Benchmark gains in coding tasks (5-6%) are consistent with generational model improvements, not a fundamentally new capability ceiling
- The worker pool is fixed at training time; newly released models require retraining or fine-tuning to be incorporated
- Intra-workflow agent isolation prevents agents from building on each other's intermediate results within a single task
- Cannot be self-contained; performance fundamentally depends on external APIs and model availability
- The Conductor training for Fugu-Ultra requires GRPO without KL penalty, which may lead to instability in some settings
- Training data mixture includes both publicly available data and expert-designed end-to-end environments

## Follow-up Work

- Integration with additional specialized models (math provers, code-specific models)
- Self-improving orchestration where the orchestrator learns to identify gaps in its worker pool
- Extension to non-coding domains like legal, medical, and scientific research workflows
- Investigation of orchestration as a complementary scaling axis to model size

---
