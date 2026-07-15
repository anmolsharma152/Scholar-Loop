---
topic: agentic-ai
difficulty: easy
tags: [llm, prompting, few-shot, chain-of-thought]
last_sent:
review_count: 0
---

# Prompt Engineering: Techniques

## Zero-Shot Prompting
Give the model a task with no examples.

```
Classify the following text as positive, negative, or neutral:
"The product works great but shipping was slow."
```

**Best for:** Simple, well-defined tasks the model already handles well.

## Few-Shot Prompting
Provide examples before the task.

```
Classify the sentiment:

Text: "I love this!" → Positive
Text: "Terrible experience." → Negative
Text: "It was okay." → Neutral

Text: "The product works great but shipping was slow." →
```

**Best for:** Custom formats, edge cases, domain-specific tasks.
**Tips:** Use 3-5 diverse examples; include edge cases; be consistent in format.

## Chain-of-Thought (CoT)
Ask the model to show its reasoning.

```
Q: If a train travels 60 mph for 2.5 hours, then 80 mph for 1.5 hours,
what is the total distance?

Let me think step by step.
Step 1: Distance = speed × time
Step 2: First segment = 60 × 2.5 = 150 miles
Step 3: Second segment = 80 × 1.5 = 120 miles
Step 4: Total = 150 + 120 = 270 miles
```

**Best for:** Math, logic, multi-step reasoning, complex analysis.
**Variants:** "Let's think step by step", "Show your reasoning", "Think carefully before answering"

## Tree-of-Thought (ToT)
Explore multiple reasoning paths; evaluate each; choose best.

```
Consider three different approaches to solve this problem:

Approach A: [reasoning]
Approach B: [reasoning]
Approach C: [reasoning]

Evaluate each approach:
A: [pros/cons]
B: [pros/cons]
C: [pros/cons]

Best approach: [selected] because [reasoning]
```

**Best for:** Complex problems where first attempt may be wrong.
**Tradeoff:** Much higher token cost; use sparingly.

## Self-Consistency
Generate multiple answers; take majority vote.

```
Generate 5 different answers to this question.
For each answer, show complete reasoning.
Then, identify the answer that appears most frequently.
```

**Best for:** Math, factual questions where there's one right answer.
**Implementation:** Call model N times with temperature > 0; vote on final answer.

## ReAct (Reason + Act)
Interleave reasoning with tool use.

```
Question: What is the population of the capital of France?

Thought: I need to find the capital of France first.
Action: search("capital of France")
Observation: Paris is the capital of France.

Thought: Now I need the population of Paris.
Action: search("population of Paris 2024")
Observation: Paris has approximately 2.1 million people.

Thought: I have the answer.
Answer: The population of Paris is approximately 2.1 million.
```
