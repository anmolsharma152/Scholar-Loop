---
topic: papers
difficulty: hard
tags: [paper, code-generation, reinforcement-learning, self-improvement, iterative-learning]
last_sent:
review_count: 0
---

# Self-Improving Code Agent via Reinforced Iterative Feedback

## Problem & Motivation
Current code generation models produce static outputs that don't improve through experience. Human developers learn from execution feedback, fix bugs, and refine their approaches iteratively—yet LLM-based coding agents operate as one-shot systems. The paper addresses how to build a self-improving agent that learns from its own successes and failures through iterative execution and reinforcement learning.

## Key Idea / Architecture
The framework has three main components:
1. **Self-Improving Agent**: Generates code for a task, executes it, evaluates correctness via unit tests, and stores the execution trace
2. **Reinforced Iterative Feedback (RIF)**: A training paradigm where the agent learns from its own execution history
   - Successful traces provide positive reinforcement
   - Failed traces provide negative signals (what went wrong)
   - Iterative refinement: the agent learns to modify code based on execution feedback
3. **Reward Model**: Trained on execution outcomes (pass/fail, test results) to score code quality
4. **RLHF-style Fine-tuning**: The base model is iteratively fine-tuned using the learned reward model

The key insight is using actual program execution as an automatic source of reward signal, eliminating the need for human feedback during training.

## Key Contributions
- Self-improving loop where code execution provides automatic reward signal
- Iterative training that progressively improves code quality through reinforcement learning
- Demonstrated that agents can learn from their own failure traces, not just successes
- The RIF paradigm achieves better performance than standard fine-tuning on static datasets
- Shows that relatively small improvements in each iteration compound over multiple rounds

## Results
- **Benchmark improvements**: Significant gains on HumanEval, MBPP, and similar coding benchmarks
- **Iterative gains**: Performance improves consistently over 3-5 rounds of self-improvement
- **Failure learning**: Learning from failures provides stronger signal than learning only from successes
- **Compounding effects**: Each iteration builds on previous improvements, creating a virtuous cycle
- **Baseline comparison**: Outperforms equivalent models trained on static curated datasets
- **Generalization**: Improvements transfer to unseen coding problems in the same domain

## Why It Matters / Impact
This work demonstrates a path toward AI systems that genuinely improve through experience rather than requiring large-scale data collection and human annotation. The automatic reward signal from code execution is a particularly elegant solution—it's objective, scalable, and directly tied to the task objective. The iterative self-improvement paradigm could extend beyond code to other domains where objective success signals exist (e.g., mathematical proof verification, robotic task completion).

## Weaknesses / Limitations
- Self-improvement is bounded by the quality of the unit test suite—bugs not caught by tests won't be learned from
- Risk of overfitting to the execution distribution: the agent may learn to exploit test patterns rather than generalize
- Iterative training requires multiple rounds of expensive execution and fine-tuning
- The approach assumes access to a reliable execution environment
- No analysis of catastrophic forgetting or reward hacking over iterations
- Limited to functional correctness; doesn't optimize for code style, readability, or efficiency
