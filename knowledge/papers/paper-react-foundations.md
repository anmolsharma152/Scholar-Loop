---
topic: papers
difficulty: hard
tags: [paper, react, llm, reasoning, agents]
last_sent:
review_count: 0
---

# ReAct: Synergizing Reasoning & Acting

**Authors:** Shunyu Yao, Jeffrey Zhao, Dian Yu, et al. (Princeton / Google)
**Published:** ICLR 2023 (arXiv 2210.03629)

## Problem

Existing LLM prompting paradigms fall into two categories:
- **Reasoning-only (CoT):** Generates a chain of thought but cannot interact with external knowledge — prone to hallucination, factually wrong.
- **Acting-only (e.g., WebGPT):** Interacts with tools/environments but generates actions without reasoning trace — needs many trial-and-error attempts.

Neither approach combines reasoning and acting, and neither learns when to stop.

## Key Idea

ReAct interleaves reasoning traces (Thought) with action execution steps (Action/Observation):

```
Question: What is the elevation range for the area where the easternmost
lowest-sitting bat species in the US lives?

Thought 1: Need to identify lowest-sitting bat species in eastern US.
Action 1: Search[lowest elevation bat species eastern United States]
Obs 1: Northern Long-eared Bat (Myotis septentrionalis) — elevation range
0-1800m

Thought 2: The bat species is the Northern Long-eared Bat. Now check
if it is the easternmost lowest-sitting species.
Action 2: Lookup[lowest elevation bat]
Obs 2: Could not find...

Thought 3: The answer is already complete.
Final Answer: 0-1800 meters
```

**Key design pattern:** The model generates "Thought: ..." (reasoning), "Action: ..." (tool call), then receives "Observation: ..." (result). This loop continues until the model emits "Final Answer: ...".

## Results

### HotpotQA (multi-hop QA)
- ReAct: 60.9% exact match (EM) with 6 reasoning traces
- CoT (no interaction): 46.3% EM
- Act (no reasoning): 54.5% EM
- ReAct + CoT fine-tuned: 73.3% EM (best)

### ALFWorld (interactive text environments)
- ReAct: 71% success rate (outperforms RL-trained agents at 48%)
- Act only: 45% success

### WebShop (online shopping)
- ReAct: 59.6% success (approaches human-level 61.1%)
- Imitation learning baseline: 59.6% (matched ReAct)
- RL-based: 56.6%
