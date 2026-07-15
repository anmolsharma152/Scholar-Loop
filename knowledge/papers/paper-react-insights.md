---
topic: papers
difficulty: hard
tags: [paper, react, llm, reasoning, agents, internal-knowledge]
last_sent:
review_count: 0
---

# ReAct: Internal Knowledge & Tool Use Tradeoff

## Key Insight
ReAct's main contribution is showing that reasoning traces and action steps are synergistic: reasoning helps with action planning (avoiding irrelevant searches), and actions provide grounding (preventing hallucination).

**Internal vs. external knowledge:** The paper found a nuanced tradeoff. For questions answerable from model parameters (e.g., common facts), CoT alone suffices and ReAct's tool calls are unnecessary. For questions requiring external knowledge (recent events, specific facts), ReAct's tool use is essential.

**The reasoning-success correlation:** ReAct actions are more likely to be correct when the preceding reasoning trace is correct (ReAct-generated Thought → correct action → correct observation → correct answer). When the reasoning trace is wrong, the action is also likely wrong. This is a form of grounding: model monitors its own reasoning validity by checking whether tool results match expectations.

## When Reasoning Alone Fails

| Failure Case | CoT | ReAct |
|---|---|---|
| Outdated knowledge (5-year-old event) | Hallucinates | Correct via search |
| Ambiguous entities ("Paris of the East") | Wrong location | Correct via definition lookup |
| Multi-step with contradictory facts | Chain breaks | Self-corrects with observations |
| Numerical calculation | Arithmetic errors | Uses calculator action |

## Limitations

1. **Action space:** Limited to search, lookup, and calculator. Real applications need diverse tool APIs.
2. **Observation parsing:** The model sometimes misparses long or complex observations
3. **Error propagation:** A wrong action leads to wrong observations, causing compounding errors
4. **Efficiency:** Multiple Thought-Action-Observation cycles increase token cost 3-5× vs CoT
5. **No learning:** Each episode is independent; ReAct doesn't accumulate experience

## Impact

ReAct was highly influential, forming the foundation for modern agent frameworks including LangChain agents and the emerging function-calling paradigm in LLM APIs. Together with Toolformer (Schick et al., 2023) and WebGPT (Nakano et al., 2021), it established the "model + tools" architecture that powers LLM agents.

**Function calling:** Modern API platforms (OpenAI, Anthropic) have adopted ReAct's core insight as built-in paradigms: the model generates structured tool calls and receives results as conversation turns.

## Follow-up

- **Reflexion (Shinn et al., 2023):** Extends ReAct with self-reflection after failures
- **ReWOO (Xu et al., 2023):** Separates reasoning from observation to reduce token cost
- **Agentic frameworks:** LangChain, AutoGPT, BabyAGI all build on ReAct-style interleaved reasoning and action
- **Tool-augmented LLMs:** Most modern LLM agents use variants of the ReAct pattern
