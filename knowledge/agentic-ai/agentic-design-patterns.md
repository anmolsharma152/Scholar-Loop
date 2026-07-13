---
topic: agentic-ai
difficulty: medium
tags: [agentic, design-patterns, llm, orchestration, tool-use]
last_sent:
review_count: 0
---

# Agentic Design Patterns

## What is an Agent?

An AI system that can:
- **Reason:** Use an LLM to plan, decide, and reflect
- **Act:** Use tools to interact with external systems
- **Observe:** Process feedback from actions
- **Iterate:** Loop through reason-act-observe until task is complete

Key distinction: Agents have agency (autonomy + goal-directed behavior), unlike simple prompt-response chains.

---

## Pattern 1: Prompt Chaining

Sequential pipeline where output of one LLM call feeds into the next.

```
Input → LLM Step 1 → LLM Step 2 → ... → LLM Step N → Output
```

**When to use:**
- Task decomposes into fixed, ordered subtasks
- Each step's output is predictable in structure
- Example: Extract info → validate → format → respond

**Tradeoffs:**
- Easy to debug (inspect each step)
- Inflexible: no branching or loops
- Latency = sum of all steps

---

## Pattern 2: Routing

Classify input and dispatch to specialized handlers.

```
Input → Router LLM → Handler A / Handler B / Handler C
```

**When to use:**
- Multiple distinct task types with different handling
- Need to optimize cost (small model for routing, large for complex)
- Example: FAQ → small model; Complex query → large model

**Implementation:**
- LLM-based classifier or fine-tuned classifier
- Rules-based router for simple cases
- Hybrid: rules for obvious cases, LLM for ambiguous

---

## Pattern 3: Parallelization

Run multiple LLM calls or tasks simultaneously.

```
         ┌→ LLM Call A ─┐
Input →  ├→ LLM Call B ─┤→ Aggregator → Output
         └→ LLM Call C ─┘
```

**When to use:**
- Independent subtasks that can execute concurrently
- Need to reduce latency (parallel beats sequential)
- Example: Evaluate from multiple perspectives; vote

**Strategies:**
- Sectioning: Split input, process in parallel, merge
- Voting: Multiple LLMs answer same question, majority wins

---

## Pattern 4: Reflection

LLM critiques and improves its own output.

```
Generate → Critique → Revise → (repeat) → Final Output
```

**When to use:**
- Quality matters more than speed
- Task benefits from self-review
- Example: Code generation + self-review + fix bugs

**Variants:**
- Self-reflection: LLM critiques its own output
- External reflection: Separate LLM critiques
- Meta-prompting: LLM evaluates if it followed instructions

---

## Pattern 5: Tool Use / Function Calling

LLM generates structured tool calls; system executes and returns results.

```
LLM decides → calls tool → receives result → continues reasoning
```

**Tool categories:**
- **Retrieval:** Search, databases, APIs
- **Computation:** Calculator, code execution, analysis
- **Action:** Send email, update DB, file operations
- **Observation:** Screenshot, web scraping, sensor data

**Implementation:**
- Define tools with JSON schema (name, description, parameters)
- LLM outputs structured function call
- Execute function, return result to LLM
- LLM continues reasoning with tool output

**Best practices:**
- Clear tool descriptions with examples
- Limit tool count to avoid confusion
- Validate tool outputs before feeding back to LLM
- Handle tool failures gracefully

---

## Pattern 6: Planning

LLM decomposes a complex goal into a sequence of subtasks.

### Planning Strategies
- **DFS (Depth-First):** Complete one subtask fully before next
- **BFS (Breadth-First):** Execute independent subtasks in parallel
- **Tree of Thought (ToT):** Explore multiple reasoning branches; evaluate and prune
- **Graph of Thought (GoT):** Non-linear reasoning with merging/splitting

**Planning components:**
1. Goal decomposition (break into steps)
2. Dependency analysis (which steps depend on others)
3. Resource allocation (which tools/agents for each step)
4. Execution with replanning (adapt when steps fail)

**Example: Research assistant**
1. Understand query → 2. Identify information gaps → 3. Plan searches
4. Execute searches → 5. Synthesize findings → 6. Generate report
7. Review and revise

---

## Pattern 7: Multi-Agent Delegation

Multiple specialized agents collaborate on complex tasks.

**Architectures:**
- **Supervisor/Worker:** One agent orchestrates; workers execute subtasks
- **Peer-to-Peer:** Agents communicate directly; no central coordinator
- **Debate:** Multiple agents argue different positions; consensus or judge decides
- **Pipeline:** Agent A → Agent B → Agent C (sequential handoff)

**When to use:**
- Task requires diverse expertise
- Subtasks are complex enough to warrant dedicated agents
- Need separation of concerns (safety, different models)

---

## Pattern 8: Memory Management

Agents maintain context across interactions.

**Memory types:**
- **Working memory:** Current conversation context (prompt window)
- **Short-term memory:** Recent interactions (summarized or sliding window)
- **Long-term memory:** Persistent knowledge (vector DB, key-value store)
- **Episodic memory:** Past experiences/tasks (what worked, what failed)

**Implementation:**
- Summarize old messages to fit context window
- Vector DB for semantic retrieval of past interactions
- Structured store for factual key-value pairs
- Cache layer for frequent queries/responses

---

## Pattern 9: Guardrails / Safety

Ensure agent behavior stays within acceptable bounds.

**Layers:**
- **Input guardrails:** Prompt injection detection, content filtering
- **Output guardrails:** Toxicity filtering, factuality checking, format validation
- **Action guardrails:** Tool call validation, sandboxed execution, human approval
- **Budget guardrails:** Token limits, cost caps, time limits

---

## Pattern 10: Evaluation and Monitoring

Measure agent performance in production.

**Metrics:**
- Task completion rate
- Tool call accuracy (correct tool, correct args)
- Latency per step and end-to-end
- Token usage and cost per task
- Human satisfaction ratings

**Methods:**
- Golden dataset with known correct outputs
- LLM-as-judge for qualitative evaluation
- A/B testing across agent architectures
- User feedback loops
