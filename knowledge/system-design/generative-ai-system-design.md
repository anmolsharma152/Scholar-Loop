---
topic: system-design
difficulty: hard
tags: [system-design, generative-ai, llm-serving, mlops, inference]
last_sent:
review_count: 0
---

# Generative AI System Design

## LLM Serving System Architecture

### Components
- **API Gateway:** Auth, rate limiting, request routing
- **Load Balancer:** Distribute across inference nodes
- **Inference Server:** vLLM, TGI, TensorRT-LLM
- **Model Registry:** Versioned model artifacts (MLflow, Weights & Biases)
- **Queue:** Async request handling (Kafka, Redis Streams)
- **Cache Layer:** Semantic/prompt caching (Redis)
- **Monitoring:** Latency, throughput, error rates, token usage

### Request Flow
1. Client → API Gateway (auth, rate limit) → Load Balancer
2. Load Balancer → Inference Worker (GPU node)
3. Inference Worker → generate tokens → stream response
4. Optional: cache hit → return cached response

---

## Prompt Management

### System Prompt Design
- Set model behavior, persona, constraints
- Version-controlled; A/B testable
- Stored in config service, not hardcoded

### Dynamic Prompt Templates
- Jinja2, Mustache templates with variables
- Input validation via Pydantic
- Chain prompts: classifier → router → specialized prompt

---

## RAG Architecture (System Design View)

### Ingestion Pipeline
1. Document ingestion (PDF, HTML, API)
2. Chunking (recursive character, semantic)
3. Embedding generation (OpenAI, Cohere, open models)
4. Vector DB indexing (Pinecone, Weaviate, Qdrant)
5. Metadata store (document store for retrieval)

### Query Pipeline
1. Query embedding
2. Similarity search (top-k)
3. Re-ranking (cross-encoder, Cohere Rerank)
4. Context assembly into prompt
5. LLM generation with retrieved context

### Design Decisions
| Decision | Options | Tradeoff |
|---|---|---|
| Embedding model | OpenAI / Cohere / open-source | Cost vs quality vs latency |
| Chunk size | 256-1024 tokens | Precision vs recall |
| Vector DB | Pinecone / Weaviate / Qdrant | Managed vs self-hosted |
| Re-ranking | Cross-encoder / ColBERT | Accuracy vs latency |
| Top-k | 3-10 | Relevance vs context window |

---

## Agent Orchestration (System Design)

### Patterns
- **Router:** Classify intent → dispatch to specialized agent
- **Supervisor:** Orchestrator agent delegates to worker agents
- **Pipeline:** Sequential chain of agents
- **Multi-agent debate:** Multiple agents reason, then aggregate

### Key Components
- **Tool Registry:** Available functions/APIs with schemas
- **Memory Store:** Short-term (conversation) + long-term (vector DB)
- **Planner:** Decomposes tasks into subtasks
- **Executor:** Runs tool calls, handles errors
- **Monitor:** Tracks agent actions, costs, latency

### Production Concerns
- Timeout and retry logic for LLM calls
- Token budget management across agent chains
- Guardrails on tool execution (sandboxing)
- Observability: log every LLM call + tool invocation

---

## Caching Strategies for LLM

### Prompt Caching
- Cache identical prompts + system prompts → reuse KV cache prefix
- Reduces prefill computation significantly
- Used by: Anthropic, OpenAI, vLLM prefix caching

### Semantic Caching
- Embed the user query → cosine similarity with cached (query, response) pairs
- Threshold > 0.95 → return cached response
- Skip LLM inference entirely for common queries

### KV Cache Optimization
- PagedAttention (vLLM): Virtual memory for KV cache
- Reduces memory fragmentation; enables higher batch sizes
- Prefix caching: Share KV cache for common prompt prefixes

---

## Cost Optimization

### Token-Level
- Use cheaper models for simple tasks (routing, classification)
- Prompt compression / summarization
- Structured outputs (reduce wasted tokens)

### Infrastructure-Level
- Spot/preemptible instances for non-urgent batch jobs
- Quantized models (GPTQ, AWQ) reduce memory → more concurrent requests
- Batch inference for offline workloads
- Autoscaling based on queue depth

### Architectural
- Semantic caching to avoid redundant inference
- Smaller models for easy queries; large models for hard ones
- RAG over fine-tuning when knowledge changes frequently

---

## Latency/Throughput Tradeoffs

| Strategy | Latency | Throughput | Use Case |
|---|---|---|---|
| Larger model | Higher | Lower | Complex reasoning |
| Smaller model | Lower | Higher | Simple tasks |
| Quantization | Lower | Higher | Cost-constrained |
| Batching | Higher (per request) | Higher | Bulk processing |
| Streaming | First token fast | Same | UX-critical |
| Caching | Very low (hit) | N/A | Repeated queries |

### Latency Budget (typical)
- API Gateway + auth: < 10ms
- RAG retrieval: < 100ms
- LLM prefill: 100-500ms (first token)
- LLM decode: 30-50ms/token
- Total acceptable for chat: < 2s first token

---

## Evaluation at Scale

- **Offline eval:** Benchmark datasets, BLEU/ROUGE, LLM-as-judge
- **Online eval:** A/B testing, human preference, proxy metrics
- **Safety eval:** Toxicity classifiers, adversarial prompts
- **Cost tracking:** Tokens per request, cost per user interaction
- **Monitoring dashboards:** Grafana/Datadog for latency, throughput, error rates
