---
topic: system-design
difficulty: hard
tags: [system-design, distributed-systems, databases, replication, consensus]
last_sent:
review_count: 0
---

# DDIA — Distributed Systems Deep Dive

## Part I: Data Systems Foundations

### Three Concerns of Data Systems
1. **Reliability:** Correct behavior despite faults
2. **Scalability:** Handling growth in load
3. **Maintainability:** Evolvability over time

### Data Models
- **Relational (tables):** Normalized, JOIN-heavy, SQL
- **Document (JSON/BSON):** Nested, denormalized, schema-flexible
- **Graph:** Nodes + edges; property graph model; Cypher/Gremlin query languages
- Each model适合 different access patterns; polyglot persistence is common

---

## Part II: Replication

### Single-Leader Replication
- One leader accepts writes; followers replicate log
- **Synchronous:** Strong consistency, higher latency
- **Asynchronous:** Better performance, risk of data loss
- **Semi-synchronous:** One sync follower + async followers
- **Replication lag problems:** Read-your-own-writes, monotonic reads, consistent prefix reads

### Multi-Leader Replication
- Multiple nodes accept writes; conflict resolution required
- **Conflict detection:** Last-write-wins (LWW), vector clocks, merge algorithms
- **Use cases:** Multi-datacenter, offline clients, collaborative editing

### Leaderless Replication
- Any node can accept writes; reads from quorum
- **Quorum:** W + R > N ensures overlap
- **Sloppy quorums + hinted handoff:** Availability during failures
- **Read repair + anti-entropy:** Background consistency recovery

---

## Part III: Partitioning

### Partitioning by Key Range
- Contiguous key ranges on each partition
- Hot spots if access patterns are skewed
- Used by: HBase, MongoDB

### Partitioning by Hash of Key
- Hash function distributes keys evenly
- Range queries become expensive
- Used by: Cassandra, DynamoDB

### Secondary Indexes in Partitions
- **Local index:** Each partition has its own secondary index; scatter-gather for queries
- **Global index:** Secondary index partitioned across nodes; more efficient reads

### Rebalancing
- **Dynamic partitioning:** Split/merge partitions as data grows
- **Fixed number of partitions:** Assign multiple partitions per node
- **Consistent hashing with virtual nodes**

---

## Part IV: Transactions

### ACID Properties
- **Atomicity:** All-or-nothing (not about concurrency)
- **Consistency:** Invariants always hold
- **Isolation:** Concurrent transactions behave as if serial
- **Durability:** Committed data survives crashes

### Isolation Levels
| Level | Dirty Reads | Non-Repeatable Reads | Phantom Reads |
|---|---|---|---|
| Read Uncommitted | Yes | Yes | Yes |
| Read Committed | No | Yes | Yes |
| Repeatable Read | No | No | Possible |
| Serializable | No | No | No |

### Implementation
- **Two-Phase Locking (2PL):** Shared/exclusive locks; pessimistic
- **MVCC (Multi-Version Concurrency Control):** Readers see snapshot; writers create versions; optimistic
- **SSI (Serializable Snapshot Isolation):** Detects write-skew anomalies; optimistic

### Single-Object vs Multi-Object
- Single-object: atomics (CAS, compare-and-set)
- Multi-object: transactions, 2PC

---

## Part V: Consistency and Consensus

### Linearizability
- Every operation appears to execute atomically at some point between invocation and response
- Strongest single-object consistency model
- Requires consensus for writes in distributed systems

### Consensus Algorithms
- **Paxos:** Classic; single-decree and multi-Paxos; complex to implement
- **Raft:** Designed for understandability; leader election, log replication, safety
- **Zab (ZooKeeper):** Similar to Raft; used in ZooKeeper
- **Viewstamped Replication (VR):** Older; similar properties

### Two-Phase Commit (2PC)
- Coordinator sends prepare → all vote yes/no → commit/abort
- **Problem:** Blocking protocol; coordinator failure blocks participants
- **Three-Phase Commit (3PC):** Non-blocking in theory; rarely used in practice

### Distributed Transactions
- **XA Transactions:** Database-level 2PC protocol
- **Saga Pattern:** Compensating transactions; eventual consistency
- **TCC (Try-Confirm-Cancel):** Application-level 2PC

---

## Part VI: Batch and Stream Processing

### Batch Processing
- **MapReduce:** Map → shuffle → reduce; fault-tolerant via re-execution
- **Hadoop ecosystem:** HDFS storage, YARN scheduling
- **Spark:** In-memory RDDs; DAG-based execution; 10-100x faster than MapReduce
- **Dataflow models:** Beam, Flink; generalized DAG with windowing

### Stream Processing
- Unbounded, continuous data processing
- **Event time vs processing time:** Out-of-order events
- **Windowing:** Tumbling, sliding, session windows
- **Watermarks:** Tracking event-time progress
- **Exactly-once semantics:** Difficult; achieved via idempotent sinks + transactional writes

### Lambda vs Kappa Architecture
- **Lambda:** Batch + stream layers; dual codebase; complexity
- **Kappa:** Stream-only; reprocess via replay; simpler but requires immutable log

---

## Key Patterns for System Design Interviews

| Pattern | Use Case |
|---|---|
| Leader election | Coordination, avoiding split-brain |
| Consistent hashing | Partitioning, load distribution |
| 2PC | Distributed transactions (avoid if possible) |
| Saga | Long-running distributed transactions |
| Event sourcing | Audit trail, temporal queries |
| CQRS | Read/write optimization separation |
| Vector clocks | Causal ordering, conflict detection |
| CRDTs | Conflict-free replicated data types |
