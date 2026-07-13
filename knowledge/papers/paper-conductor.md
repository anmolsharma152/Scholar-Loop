---
topic: papers
difficulty: hard
tags: [paper, ensemble, reasoning, multi-model, orchestration, diversity, language-models]
last_sent:
review_count: 0
---

# Conductor: A Chorus of LLMs Orchestrates Diverse Reasoning Paths

## Problem & Motivation
Single LLMs face a fundamental diversity bottleneck—each architecture encodes particular inductive biases, limiting the range of reasoning strategies it can deploy. Prior ensemble methods like self-consistency rely on homogeneous reasoning from one model, or heterogeneous voting that treats all models equally without accounting for expertise differences. The question: can we systematically orchestrate diverse LLMs to produce better reasoning than any single model?

## Key Idea / Architecture
A three-component ensemble framework:
1. **Conductor** (planner): A lightweight classifier that decomposes multi-hop questions into subproblems and assigns each to the best-suited expert based on a learnable router
2. **Experts**: A heterogeneous collection of LLMs (e.g., Phi-3-mini, Gemma-2, Mistral-7B, Qwen2.5)
3. **Synthesizer**: Merges partial solutions from experts into a coherent final answer

The router is trained on question-subproblem-expert triples using a small set of 50-100 human-annotated examples. The Conductor itself is lightweight (~7B parameters), while experts can be larger.

## Key Contributions
- Demonstrated that orchestrated multi-model reasoning outperforms self-consistency (single model sampling) across five benchmarks
- The Conductor planner alone (without experts) sometimes matches or exceeds larger models like GPT-4o
- Showed that diverse model ensembles outperform same-model ensembles even when individual experts are smaller
- Introduced a learnable routing mechanism that assigns subproblems to appropriate expert architectures
- Strong performance in mathematical reasoning (MathVista: 85.2% vs. 82.1% for self-consistency)

## Results
- **MathVista**: Conductor 85.2% vs. Self-Consistency 82.1% (Phi-3-mini as base)
- **MathQA**: Conductor 71.9% vs. SC 69.3% (Phi-3-mini base)
- **ARC-Challenge**: Conductor 76.4% vs. SC 73.2% (Phi-3-mini base)
- **HumanEval**: Conductor 71.2% vs. SC 68.5% (Phi-3-mini base)
- **Win Rate vs. GPT-4o**: Consistently outperformed across math reasoning benchmarks
- **Efficiency**: Uses only 1/4 to 1/10 the parameters of a comparable GPT-4o-scale model
- **Generalization**: Performance improves as more diverse experts are added

## Why It Matters / Impact
Conductor challenges the assumption that a single monolithic model is the optimal approach. By explicitly modeling the routing of subproblems to specialized experts, it achieves performance comparable to or exceeding much larger models with significantly fewer parameters. The framework is modular—new experts can be added without retraining the conductor. This has implications for building cost-effective, high-performing AI systems that leverage the strengths of multiple specialized models.

## Weaknesses / Limitations
- Requires maintaining and running multiple models simultaneously (increased infrastructure cost)
- Router training depends on quality of human-annotated routing examples
- Performance ceiling is bounded by the available expert pool
- The overhead of coordinating multiple models may negate parameter efficiency gains at inference time
- Limited evaluation on non-English tasks
- No analysis of failure modes when experts disagree on subproblem solutions
