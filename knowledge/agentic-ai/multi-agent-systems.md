---
topic: agentic-ai
difficulty: hard
tags: [agentic, multi-agent, coordination, planning, llm]
last_sent:
review_count: 0
---

# Multi-Agent Systems

## What is a Multi-Agent System?

A system where multiple AI agents (LLM-powered) collaborate to solve complex tasks. Each agent has its own role, tools, memory, and reasoning loop.

**Why multiple agents?**
- Complex tasks require diverse expertise
- Separation of concerns (planning vs execution vs review)
- Parallel processing of independent subtasks
- Different models for different tasks (cheap for routing, powerful for reasoning)

---

## Taxonomy of Multi-Agent Orchestration Patterns

### Workflow Patterns (Explicit Control)

**1. Prompt Chaining (Sequential)**
- Agent A output → Agent B input → Agent C input
- Fixed, predictable flow
- Easy to debug; inflexible

**2. Routing / Classifier**
- Router agent classifies input → dispatches to specialist agents
- Cost optimization: small model routes, large model executes

**3. Parallelization**
- Independent agents process simultaneously
- Sectioning: divide input, process in parallel, merge results
- Voting: multiple agents answer same question, aggregate

**4. Orchestrator-Workers**
- Central orchestrator LLM decomposes task → assigns to worker agents
- Orchestrator synthesizes results
- Workers are stateless; orchestrator holds state

**5. Evaluator-Optimizer**
- Generator agent produces output
- Evaluator agent critiques output
- Loop until quality threshold met

### Autonomous Patterns (Emergent Control)

**6. Agent Chat / Debate**
- Multiple agents discuss; emergent behavior from interaction
- Can lead to better reasoning through disagreement
- Risk: hallucination amplification, infinite loops

**7. Decentralized / Market-Based**
- Agents bid on tasks based on capability
- No central coordinator
- Inspired by economics and swarm intelligence

---

## Agent Communication

### Communication Models
- **Direct:** Agent-to-agent message passing
- **Blackboard:** Shared knowledge store all agents read/write
- **Event-driven:** Pub/sub; agents subscribe to events
- **Supervisor-mediated:** All communication through orchestrator

### Message Formats
- Structured JSON with schema
- Natural language (flexible but harder to parse)
- Hybrid: structured envelope + natural language payload

### Protocols
- **A2A (Agent-to-Agent):** Google's protocol for cross-framework agent communication
- **MCP (Model Context Protocol):** Standard for tool/data access
- Request-response, publish-subscribe, broadcast

---

## Coordination Mechanisms

### Task Allocation
- **Static assignment:** Predefined roles (researcher, writer, reviewer)
- **Dynamic assignment:** Orchestrator evaluates agent capabilities and assigns
- **Auction-based:** Agents bid on tasks; highest capability/willingness wins

### Synchronization
- **Barrier:** Wait for all agents to complete before proceeding
- **Semaphore:** Limit concurrent agents on shared resource
- **Token passing:** Agent holds token → can act; passes to next

### Conflict Resolution
- **Voting:** Majority decision
- **Mediator:** Designated agent resolves conflicts
- **Priority:** Higher-ranked agent's decision wins
- **Consensus:** All agents must agree (slow but robust)

---

## Supervisor/Worker Pattern (Most Common)

```
                    ┌─ Research Agent (tools: web search, APIs)
Supervisor Agent ──├─ Code Agent (tools: code interpreter, files)
                    └─ Review Agent (tools: validator, linter)
```

### Supervisor Responsibilities
- Decompose user request into subtasks
- Assign subtasks to appropriate workers
- Collect and synthesize results
- Handle errors and retries
- Manage conversation state

### Worker Responsibilities
- Execute assigned subtask with specialized tools
- Return structured results to supervisor
- Report errors and limitations

### Implementation Pattern
```python
class SupervisorAgent:
    def __init__(self, workers: dict[str, Agent]):
        self.workers = workers

    async def handle(self, request: str):
        plan = await self.plan(request)
        results = {}
        for step in plan.steps:
            worker = self.workers[step.agent]
            results[step.id] = await worker.execute(step.task, context=results)
        return await self.synthesize(results)
```

---

## Debate Pattern

Multiple agents argue different positions; a judge or voting mechanism decides.

**Use cases:**
- Complex reasoning that benefits from multiple perspectives
- Fact-checking and verification
- Creative tasks needing diverse ideas

**Risks:**
- Agents may reinforce each other's errors (echo chamber)
- High token cost (multiple agents × multiple rounds)
- Difficulty determining "winner"

---

## Tool Sharing

- Centralized tool registry accessible to all agents
- Each agent declares its available tools
- Orchestrator routes tool calls to appropriate agent
- Shared tools need concurrency control (rate limits, locks)

---

## Memory Management in Multi-Agent Systems

### Shared Memory
- Blackboard pattern: all agents read/write shared state
- Risk: race conditions, conflicting updates
- Use versioned entries or transactional updates

### Agent-Private Memory
- Each agent maintains its own conversation history
- Useful for specialized agents with different context needs
- May need summarization to manage context window

### Cross-Agent Knowledge Transfer
- Agent A discoveries → stored in shared memory → Agent B retrieves
- Episodic memory: "In task X, approach Y worked well"
- Deduplication and conflict resolution needed

---

## Production Considerations

### Reliability
- Idempotent agent operations (retry-safe)
- Circuit breakers for failing agents
- Fallback agents for each role
- Maximum step limits to prevent infinite loops

### Observability
- Log every agent's input, output, tool calls
- OpenTelemetry integration for distributed tracing
- Token usage and cost tracking per agent
- Latency breakdown by agent

### Cost Control
- Token budgets per agent and per task
- Cheaper models for simple agents (routing, classification)
- Caching for repeated queries across agents
- Budget alerts and circuit breakers

### Testing
- Unit test individual agents
- Integration test agent interactions
- End-to-end test with golden datasets
- Stress test with high concurrency

---

## Frameworks Comparison

| Framework | Pattern | Key Feature |
|---|---|---|
| LangGraph | Graph-based workflows | State machines, checkpointing |
| CrewAI | Role-based crews | Simple role definition |
| AutoGen | Conversational agents | Multi-agent chat |
| Swarm | Handoff-based | Lightweight, agent transfer |
| Semantic Kernel | Plugin-based | Enterprise integration |
