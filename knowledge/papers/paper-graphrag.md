---
topic: papers
difficulty: hard
tags: [paper, graphrag, retrieval-augmented-generation, graphs, knowledge-graphs]
---

# Retrieval-Augmented Generation with Graphs (GraphRAG)

**Authors:** Han et al. (Michigan State, Oregon, Amazon, Meta)
**Published:** 2025
**arXiv:** 2501.00309

## Problem & Motivation

Standard RAG uses text/image retrieval but ignores relational structure in data:
1. **No relational reasoning** - Can't leverage entity relationships
2. **Fragmented information** - Documents are independent, no connections
3. **Domain-specific challenges** - Different domains need different designs

Graphs naturally encode relational information. The question: how can we integrate graphs into RAG?

## Key Idea / Architecture

### GraphRAG Framework

A holistic framework with 5 components:

1. **Query Processor:** Transforms text queries to graph-aware queries
2. **Graph Data Source:** Structured relational information
3. **Retriever:** Graph-aware retrieval
4. **Organizer:** Arranges retrieved content
5. **Generator:** Produces final answer

### Unique Challenges of Graph Data

**Diverse formats:**
- Knowledge graphs: Triplets, paths
- Document graphs: Sentence chunks
- Molecule graphs: Higher-order structures

**Interdependent information:**
- Graph edges connect related content
- Multi-hop reasoning required
- Structural relationships matter

**Domain-specific:**
- Relations vary by domain
- No universal graph representation
- Different tasks need different approaches

### Graph Retrieval Methods

**Heuristic-based:**
- Entity linking (map text to graph nodes)
- Relational matching (find related edges)
- Graph traversal (BFS, DFS)
- Graph kernels (structural similarity)

**Learning-based:**
- Graph Neural Networks (GNNs)
- Shallow embeddings
- Deep embeddings

**Domain-specific:**
- Expert rules
- Domain knowledge

### Query Processing

1. **Named Entity Recognition:** Extract entities from query
2. **Relational Extraction:** Identify relationships
3. **Query Structuration:** Convert to graph query (GQL, SPARQL)
4. **Query Decomposition:** Split into sub-queries
5. **Query Expansion:** Add semantically similar terms

## Key Contributions

1. **Holistic framework** - Unified view of GraphRAG components
2. **Domain specialization** - Tailored approaches for different domains
3. **Comprehensive survey** - Covers 10+ domains and hundreds of papers
4. **Future directions** - Identifies research challenges and opportunities

## Applications by Domain

### Knowledge Graphs
- Question answering
- KG completion
- Fact checking

### Document Graphs
- Document summarization
- Document classification
- Relational extraction

### Scientific Graphs
- Molecule generation
- Property prediction
- Drug discovery

### Social Graphs
- Recommendation
- Fake news detection
- Community detection

### Reasoning Graphs
- Planning
- Tool usage
- Embodied agents

## Why It Matters

GraphRAG is important because:

1. **Relational reasoning** - Enables reasoning over relationships
2. **Structured knowledge** - Leverages existing graph databases
3. **Domain applicability** - Useful across many domains
4. **Foundation for future** - Graphs + LLMs is a growing area

## Weaknesses

- **Complexity** - Graph methods are more complex than text retrieval
- **Scalability** - Graph traversal can be expensive
- **Domain specificity** - Hard to create universal methods
- **Evaluation** - Limited standardized benchmarks

## Follow-up Work

- **Microsoft GraphRAG:** Community detection for document retrieval
- **Knowledge graph QA:** Specialized methods for KG question answering
- **Molecular GraphRAG:** Drug discovery applications
- **Social GraphRAG:** Recommendation and social network analysis