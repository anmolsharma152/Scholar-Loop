---
topic: papers
difficulty: hard
tags: [paper, agentic-rag, retrieval-augmented-generation, agents, tool-use]
---

# Agentic Retrieval-Augmented Generation: A Survey on Agentic RAG

**Authors:** Survey paper
**Published:** 2024

## Problem & Motivation

Standard RAG has limitations:
1. **Passive retrieval** - Retrieves once, doesn't adapt
2. **No reasoning** - Can't plan retrieval strategies
3. **No tool use** - Limited to single retrieval method
4. **No verification** - Can't verify retrieved information

Agentic RAG makes RAG active and intelligent by adding agency.

## Key Idea / Architecture

### What is Agentic RAG?

RAG systems enhanced with:
- **Planning** - Decide what to retrieve and when
- **Tool use** - Use multiple retrieval strategies
- **Reasoning** - Plan multi-step retrieval
- **Reflection** - Evaluate and improve retrieval
- **Adaptation** - Adjust strategy based on results

### Core Components

1. **Agent:** LLM-based controller that plans and executes
2. **Tools:** Different retrieval methods (search, DB, APIs)
3. **Memory:** Store past retrievals and results
4. **Planning:** Multi-step retrieval strategies
5. **Reflection:** Evaluate retrieval quality

### Types of Agentic RAG

**Single-agent:**
- One agent controls retrieval and generation
- Can use multiple tools
- Simpler to implement

**Multi-agent:**
- Multiple agents collaborate
- Specialized agents for different tasks
- More complex but more capable

**Hierarchical:**
- Manager agent delegates to worker agents
- Different levels of abstraction
- Scalable for complex tasks

### Key Patterns

**Iterative retrieval:**
1. Initial retrieval
2. Analyze results
3. Refine query
4. Retrieve again
5. Generate answer

**Tool-augmented:**
1. Analyze query
2. Select appropriate tool
3. Execute tool
4. Process results
5. Generate answer

**Collaborative:**
1. Multiple agents discuss query
2. Each contributes expertise
3. Synthesize results
4. Generate answer

## Key Contributions

1. **Comprehensive survey** - Covers all aspects of Agentic RAG
2. **Taxonomy** - Clear classification of approaches
3. **Applications** - Real-world use cases
4. **Future directions** - Research challenges and opportunities

## Applications

### Enterprise
- Document analysis with multiple sources
- Code generation with documentation
- Data analysis with database queries

### Research
- Literature review with paper search
- Experimental design with method retrieval
- Hypothesis generation with knowledge synthesis

### Customer Service
- Multi-turn conversation with context
- Tool use for account operations
- Escalation and verification

### Healthcare
- Medical question answering
- Clinical decision support
- Drug interaction checking

## Why It Matters

Agentic RAG represents the future of retrieval-augmented systems:

1. **Active retrieval** - More intelligent information gathering
2. **Multi-step reasoning** - Can handle complex queries
3. **Tool integration** - Leverages multiple information sources
4. **Self-improvement** - Can learn from mistakes

## Weaknesses

- **Complexity** - Much more complex than standard RAG
- **Latency** - Multiple retrieval steps increase response time
- **Cost** - LLM calls for planning and reasoning are expensive
- **Error propagation** - Mistakes in planning compound

## Follow-up Work

- **AutoGen:** Framework for multi-agent systems
- **LangGraph:** Agent-based RAG frameworks
- **Tool-augmented LLMs:** Models that learn to use tools
- **Self-reflective RAG:** Systems that evaluate their own retrieval