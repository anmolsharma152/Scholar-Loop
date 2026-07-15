---
topic: agentic-ai
difficulty: medium
tags: [rag, retrieval, vector-databases, embeddings, chunking]
last_sent:
review_count: 0
---

# RAG Systems: Ingestion & Retrieval

## RAG Overview

**Retrieval-Augmented Generation (RAG):** Combine LLM generation with external knowledge retrieval.

User Query → Retrieval → Context Assembly → LLM Generation → Response

**Why RAG over fine-tuning?**
- Knowledge changes frequently (no retraining needed)
- Traceable: can cite sources
- Cheaper: no GPU training required
- Flexible: swap retrieval backend without changing model

## Ingestion Pipeline

### 1. Document Loading
- Supported formats: PDF, DOCX, HTML, Markdown, CSV, code files
- Handle tables, images (OCR), embedded metadata

### 2. Chunking Strategies

| Strategy | Chunk Size | Overlap | Best For |
|---|---|---|---|
| Fixed-size | 256-1024 tokens | 50-200 tokens | Simple, fast |
| Recursive character | Variable | Overlap zone | Natural text |
| Semantic chunking | Varies | None | Topic boundaries |
| Document-based | Per section/heading | None | Structured docs |
| Code-aware | Per function/class | None | Codebases |

**Key decisions:** Small chunks (256) give high precision but may lose context. Large chunks (1024+) give more context but may dilute relevance. Overlap prevents information loss at boundaries.

### 3. Embedding Generation

Models include OpenAI text-embedding-3 (1536/3072 dims), Cohere embed-v3, BGE (open-source), E5-Mistral (state-of-the-art), Jina embeddings. Dimensions range from 384-3072 with a tradeoff between quality and storage/search speed.

### 4. Vector Database Indexing

Index types: Flat (brute force, O(N)), IVF (cluster vectors into partitions), HNSW (graph-based, O(log N), best recall/speed), PQ (compress vectors), IVF-PQ (hybrid). Key HNSW parameters: M (connections per node), ef_construction (build-time search width), ef_search (query-time search width).

Popular vector DBs: Pinecone, Weaviate (HNSW), Qdrant (Rust, fast), Milvus (GPU support), Chroma (lightweight), pgvector (Postgres extension), FAISS (library, Meta).

## Retrieval Methods

**Dense retrieval:** Embed query → cosine similarity with document embeddings. Captures semantic meaning but weak on rare terms and exact matches.

**Sparse retrieval:** BM25 or TF-IDF. Strong on exact keyword matching, weak on semantic understanding.

**Hybrid retrieval:** Combine dense + sparse scores using Reciprocal Rank Fusion (RRF). Typically 5-15% improvement over either alone. Best practice: always use hybrid.

**Re-ranking:** Cross-encoder (BERT-like) scores (query, doc) pairs. Higher quality than bi-encoder similarity but slower. Use on top-k from initial retrieval. Tools: Cohere Rerank, bge-reranker.
