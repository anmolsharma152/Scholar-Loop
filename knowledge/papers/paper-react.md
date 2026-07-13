---
topic: papers
difficulty: hard
last_sent:
review_count: 0
tags:
  - paper
  - reasoning
  - language-models
  - chain-of-thought
  - action
---

# ReAct: Synergizing Reasoning and Acting in Language Models

**Authors:** Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, Yuan Cao (Princeton, Google Brain)
**Published:** International Conference on Learning Representations (ICLR) 2023
**arXiv:** 2210.03629

## Problem & Motivation

Large language models excel at either chain-of-thought (CoT) reasoning or acting in environments (selecting actions and observing results), but not both simultaneously. CoT methods (Wei et al., 2022) decompose problems into reasoning traces but operate purely in internal knowledge, making them prone to hallucination when factual grounding is needed. Acting methods (Toolformer, WebGPT) select actions based on environment observations but lack explicit reasoning about *why* those actions are chosen, leading to low sample efficiency and poor generalization to novel situations. The challenge was to create a framework that alternates between reasoning (verbalizing thought processes) and acting (interacting with environments), allowing the model to maintain both coherence and groundedness.

## Key Idea / Architecture

ReAct interleaves three types of utterances in a single trajectory: **Thought** (verbal reasoning about current state and planning), **Action** (structured interaction with an external environment), and **Observation** (environment response). These alternate in the pattern: Thought₁ → Action₁ → Observation₁ → Thought₂ → Action₂ → ...

**Thought component:** The model generates a natural language thought that analyzes the current state, reasons about what information is needed, and plans the next action. Thoughts serve as: (1) a scratchpad for working memory, (2) a reasoning chain that decomposes multi-step problems, and (3) a mechanism for incorporating domain knowledge into decision-making.

**Action component:** Actions are formatted as API calls or structured commands specific to the environment. For knowledge tasks: Search[query], Lookup[term], Finish[answer]. For decision-making: Walk[location], Buy[item], SearchObject[object]. Actions are validated against the environment's API before execution.

**Observation component:** The environment returns the result of the action—search results, page content, location descriptions, error messages. These observations are appended to the trajectory and inform subsequent reasoning.

**Training:** ReAct is trained on few-shot demonstrations (typically 3-10 examples) where human annotators write Thought-Action-Observation trajectories. The model is a frozen language model (PaLM 540B, GPT-3 175B, or fine-tuned PaLM-LoRA 8B) with in-context learning. No reinforcement learning or fine-tuning on trajectories is required.

**Decoding:** At each step, the model generates the next Thought/Action token sequence autoregressively. When an Action token matches a valid environment action, execution pauses and the observation is appended. The model then continues generating. For parallel actions (e.g., multiple search queries), a special `[SEP]` token separates independent action-observation pairs.

**Trajectory format example (HotpotQA):**
```
Thought 1: I need to search for the 40th U.S. president and his birth year.
Action 1: Search[40th President of the United States]
Observation 1: Ronald Wilson Reagan (February 6, 1911 – June 5, 2004)
Thought 2: The 40th president was Ronald Reagan, born February 6, 1911. Let me verify his age.
Action 2: Search[age of Ronald Reagan when he became president]
Observation 2: Reagan was 69 when inaugurated on January 20, 1981.
Thought 3: Reagan was 69 when becoming president. Answer: 69.
Action 3: Finish[69]
```

## Key Contributions

1. Novel framework interleaving reasoning traces (Thoughts) with environment interactions (Actions and Observations) in a single coherent trajectory.
2. Demonstration that reasoning and acting are complementary: reasoning enables better action selection, while observations ground reasoning in factual evidence.
3. Zero-shot generalization to unseen tasks by simply changing the environment/API definition while keeping the ReAct format constant.
4. Analysis showing ReAct reduces hallucination: 78% of facts in ReAct traces come from environment observations vs. 22% from model's internal knowledge.
5. Open-source ReAct prompt library and benchmark suite for reproducible evaluation.

## Results (Specific Numbers)

**HotpotQA (multi-hop question answering):**
- ReAct EM (exact match): 27.5%
- Chain-of-thought: 19.4%
- Act-only (no reasoning): 22.6%
- ReAct improves over CoT by +8.1 points and over Act-only by +4.9 points

**FEVER (fact verification):**
- ReAct accuracy: 60.9%
- Chain-of-thought: 56.3%
- Act-only: 58.2%
- +4.6 points over CoT, +2.7 over Act-only

**ALFWorld (interactive decision-making):**
- ReAct success rate: 71%
- Act-only (no reasoning): 61%
- Thought-less (no Thoughts): 56%
- ReAct achieves the highest success rate with fewer repeated actions

**Multi-Action Trajectories:**
- ReAct generates average 3.2 thought-action pairs per question on HotpotQA
- Multi-step ReAct trajectories contain 100% more correct intermediate steps than single-step reasoning
- Hallucination rate drops from 38% (CoT) to 22% (ReAct) for factual claims

**Efficiency:**
- ReAct uses ~4-8x more tokens than CoT (due to environment observations) but achieves 40% better accuracy
- ReAct with PaLM-LoRA 8B: 17.9% EM on HotpotQA (vs. 12.3% for CoT at same model size)

## Why It Matters / Impact

ReAct established the reasoning-acting paradigm that underpins modern LLM agents (AutoGPT, LangChain agents, OpenAI Assistants API, Claude Computer Use). The insight that language models benefit from explicit reasoning about *what to do next*—combined with environmental feedback—became foundational for agentic AI systems. The framework demonstrated that in-context learning alone (without RL fine-tuning) could produce effective agents for knowledge-intensive and interactive tasks.

## Weaknesses / Limitations

1. ReAct requires an environment API; the approach does not apply to purely internal reasoning tasks where no external tools are available.
2. Performance depends heavily on the quality of few-shot demonstrations; poorly written trajectories can mislead the model.
3. Error propagation: an incorrect thought early in the trajectory can compound, leading the model to take irrelevant actions for many steps.
4. ReAct is significantly more expensive than CoT due to environment interactions (search API calls, page loads), with each question requiring 3-8 external API calls.
5. The framework assumes a sequential environment; parallel or concurrent action execution is not well supported.

## Follow-up Work

- Reflexion (Yao et al., 2023): Adds self-reflection after failed trajectories, allowing iterative improvement.
- Toolformer (Schick et al., 2023): Learns to use tools without explicit ReAct formatting via self-supervised training.
- LangChain/LlamaIndex: Production frameworks implementing ReAct-style agent loops with various tool integrations.
- Claude Computer Use: Anthropic's implementation of ReAct for GUI interaction, demonstrating the paradigm's generalizability.
