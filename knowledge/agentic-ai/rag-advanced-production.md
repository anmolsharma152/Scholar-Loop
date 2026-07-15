---
topic: agentic-ai
difficulty: medium
tags: [rag, advanced-rag, evaluation, production]
last_sent:
review_count: 0
---

# RAG Systems: Advanced Patterns & Production

## Query Transformation

Techniques to improve retrieval:
- **Query rewriting:** LLM rephrases for better retrieval
- **HyDE (Hypothetical Document Embedding):** Generate hypothetical answer, embed that, then retrieve based on the hypothetical document
- **Step-back prompting:** Broaden query for context; narrow for specific
- **Sub-question decomposition:** Break complex query into sub-queries
- **Query expansion:** Add synonyms or related terms

## Context Assembly Strategies

- **Stuffing:** All retrieved chunks into one prompt (simplest)
- **Map-reduce:** Process each chunk independently, then aggregate
- **Refine:** Iteratively refine answer with each chunk

**Context window management:** Rank by relevance score; take top-k that fit in context. Summarize low-ranking chunks instead of dropping. Reserve space for system prompt + few-shot examples.

## Advanced RAG Patterns

**Agentic RAG:** Agent decides when/what to retrieve. Can perform multiple retrieval rounds. Self-corrects: if answer is insufficient, retrieves again. Uses tools: vector search, SQL, web search, APIs.

**Corrective RAG (CRAG):** Retrieve → Evaluate relevance → Decide action. If relevant: extract key info; use for generation. If ambiguous: web search to supplement. If irrelevant: web search only.

**Self-RAG:** Model generates retrieval query token when it needs info. Judges whether retrieved context is relevant and whether generated answer is supported by context. Trained to self-reflect on each step.

## RAG Evaluation

**Retrieval metrics:** Recall@k, Precision@k, MRR, NDCG
**Generation metrics:** Faithfulness, relevancy, answer correctness
**End-to-end:** Human preference, A/B testing

**Frameworks:** RAGAS, TruLens, DeepEval

**Key quality dimensions:**
1. Context relevancy: Retrieved chunks are relevant to query
2. Faithfulness: Answer is grounded in retrieved context
3. Answer relevancy: Answer addresses the query
4. Context recall: All needed information was retrieved

## Production Checklist

- [ ] Chunk size optimized (test 256, 512, 1024)
- [ ] Hybrid retrieval (dense + sparse) enabled
- [ ] Re-ranking step included
- [ ] Query transformation for complex queries
- [ ] Source citations in responses
- [ ] Evaluation pipeline (RAGAS or similar)
- [ ] Monitoring: retrieval latency, relevance scores
- [ ] Feedback loop: human ratings improve retrieval
- [ ] Cost tracking: embedding API calls, vector DB ops
