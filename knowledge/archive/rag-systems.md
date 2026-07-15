---
topic: agentic-ai
difficulty: medium
tags: [rag, retrieval, vector-databases, embeddings, chunking]
last_sent:
review_count: 0
---

# RAG Systems — Deep Dive

## RAG Overview

**Retrieval-Augmented Generation (RAG):** Combine LLM generation with external knowledge retrieval.

```
User Query → Retrieval → Context Assembly → LLM Generation → Response
```

**Why RAG over fine-tuning?**
- Knowledge changes frequently (no retraining needed)
- Traceable: can cite sources
- Cheaper: no GPU training required
- Flexible: swap retrieval backend without changing model

---

## Ingestion Pipeline

### 1. Document Loading
- Supported formats: PDF, DOCX, HTML, Markdown, CSV, code files
- Tools: LangChain loaders, Unstructured, LlamaIndex readers
- Handle: tables, images (OCR), embedded metadata

### 2. Chunking Strategies

| Strategy | Chunk Size | Overlap | Best For |
|---|---|---|---|
| Fixed-size | 256-1024 tokens | 50-200 tokens | Simple, fast |
| Recursive character | Variable | Overlap zone | Natural text |
| Semantic chunking | Varies | None | Topic boundaries |
| Document-based | Per section/heading | None | Structured docs |
| Code-aware | Per function/class | None | Codebases |
| Agentic chunking | LLM-determined | None | Highest quality |

**Key decisions:**
- Small chunks (256): High precision, may lose context
- Large chunks (1024+): More context, may dilute relevance
- Overlap: Prevents information loss at boundaries

### 3. Embedding Generation

**Models:**
- **OpenAI text-embedding-3:** 1536/3072 dims; best general quality
- **Cohere embed-v3:** Multilingual; short doc optimized
- **BGE (BAAI):** Open-source; competitive with closed models
- **E5-Mistral:** LLM-based embeddings; state-of-the-art retrieval
- **Jina embeddings:** Long context; multilingual

**Dimensions:** 384-3072; tradeoff between quality and storage/search speed

### 4. Vector Database Indexing

**Index types:**
- **Flat (brute force):** Exact search; O(N); small datasets only
- **IVF (Inverted File):** Cluster vectors into partitions; search nearest clusters
- **HNSW (Hierarchical Navigable Small World):** Graph-based; O(log N); best recall/speed
- **PQ (Product Quantization):** Compress vectors; memory-efficient
- **IVF-PQ:** Hybrid; good for very large datasets

**HNSW Parameters:**
- `M`: Number of connections per node (higher = better recall, more memory)
- `ef_construction`: Build-time search width (higher = better graph quality)
- `ef_search`: Query-time search width (higher = better recall, slower)

**Vector Database Comparison:**

| Database | Index | Managed | Notable |
|---|---|---|---|
| Pinecone | Proprietary | Yes | Serverless, pay-per-use |
| Weaviate | HNSW | Both | GraphQL API, modules |
| Qdrant | HNSW | Both | Rust, fast, filtering |
| Milvus | IVF/HNSW/PQ | Both | GPU support, massive scale |
| Chroma | HNSW | Self-host | Lightweight, developer-friendly |
| pgvector | IVFFlat/HNSW | Postgres extension | Existing Postgres infra |
| FAISS | IVF/HNSW/PQ | Library | Meta; fastest at scale |

---

## Retrieval Methods

### Dense Retrieval
- Embed query → cosine similarity with document embeddings
- Captures semantic meaning (not keyword matching)
- Weak on: rare terms, exact matches, acronyms

### Sparse Retrieval
- BM25 or TF-IDF based
- Strong on: exact keyword matching, rare terms
- Weak on: synonymy, semantic understanding

### Hybrid Retrieval
- Combine dense + sparse scores
- Reciprocal Rank Fusion (RRF) to merge rankings
- Typically 5-15% improvement over either alone
- Best practice: always use hybrid

### Re-ranking
- **Cross-encoder:** BERT-like model scores (query, doc) pairs
- Higher quality than bi-encoder similarity
- Slower; use on top-k from initial retrieval
- Tools: Cohere Rerank, bge-reranker, cross-encoder/ms-marco

---

## Query Transformation

### Techniques
- **Query rewriting:** LLM rephrases for better retrieval
- **HyDE (Hypothetical Document Embedding):** Generate hypothetical answer, embed that
- **Step-back prompting:** Broaden query for context; narrow for specific
- **Sub-question decomposition:** Break complex query into sub-queries
- **Query expansion:** Add synonyms or related terms

### When to Use
- Ambiguous queries → query rewriting
- Need broader context → step-back
- Multi-hop questions → sub-question decomposition

---

## Context Assembly

### Strategies
- **Stuffing:** All retrieved chunks into one prompt (simplest)
- **Map-reduce:** Process each chunk independently, then aggregate
- **Refine:** Iteratively refine answer with each chunk
- **Split-merge:** Split large contexts, process, merge

### Context Window Management
- Rank by relevance score; take top-k that fit in context
- Summarize low-ranking chunks instead of dropping
- Reserve space for system prompt + few-shot examples

---

## Advanced RAG Patterns

### Agentic RAG
- Agent decides when/what to retrieve
- Can perform multiple retrieval rounds
- Self-corrects: if answer is insufficient, retrieves again
- Uses tools: vector search, SQL, web search, APIs

### Corrective RAG (CRAG)
- Retrieve → Evaluate relevance → Decide action
- If relevant: extract key info; use for generation
- If ambiguous: web search to supplement
- If irrelevant: web search only

### Self-RAG
- Model generates retrieval query token when it needs info
- Judges whether retrieved context is relevant
- Judges whether generated answer is supported by context
- Trained to self-reflect on each step

---

## RAG Evaluation

### Metrics
- **Retrieval metrics:** Recall@k, Precision@k, MRR, NDCG
- **Generation metrics:** Faithfulness, relevancy, answer correctness
- **End-to-end:** Human preference, A/B testing

### Frameworks
- **RAGAS:** Retrieval and generation evaluation
- **TruLens:** Feedback functions for LLM apps
- **DeepEval:** LLM evaluation metrics

### Key Quality Dimensions
1. **Context relevancy:** Retrieved chunks are relevant to query
2. **Faithfulness:** Answer is grounded in retrieved context
3. **Answer relevancy:** Answer addresses the query
4. **Context recall:** All needed information was retrieved

---

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
