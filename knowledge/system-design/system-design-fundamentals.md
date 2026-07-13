---
topic: system-design
difficulty: medium
tags: [system-design, fundamentals, scalability, distributed-systems]
last_sent:
review_count: 0
---

# System Design Fundamentals

## Scale From Zero to Millions of Users

### Vertical Scaling (Scale Up)
- Upgrade machine: more CPU, RAM, disk
- Single point of failure; practical ceiling on hardware
- Good starting point for small apps

### Horizontal Scaling (Scale Out)
- Add more servers behind a load balancer
- No hard ceiling; fault-tolerant with replication
- Requires stateless application design

---

## Load Balancing

### Algorithms
- **Round Robin:** Cycle through servers sequentially
- **Weighted Round Robin:** Assign more requests to higher-capacity servers
- **Least Connections:** Route to server with fewest active connections
- **IP Hash:** Consistent routing based on client IP

### L4 vs L7 Load Balancers
- **L4 (Transport):** Route based on IP + port; faster, less inspectable
- **L7 (Application):** Route based on HTTP headers/URL; enables content-based routing, SSL termination

### Placement
- DNS round-robin to place LBs at edge
- Active-passive or active-active HA pairs

---

## Caching

### Where to Cache
- **Browser caching:** `Cache-Control`, `ETag` headers
- **CDN caching:** Static assets at edge
- **Application caching:** Redis/Memcached in front of DB
- **Database query caching:** Built-in DB query cache

### Cache Strategies
- **Cache-Aside (Lazy Loading):** App checks cache first; miss → read DB → populate cache
- **Write-Through:** Write to cache + DB simultaneously
- **Write-Behind (Write-Back):** Write to cache; async flush to DB
- **Refresh-Ahead:** Proactively refresh cache before expiry

### Eviction Policies
- LRU (Least Recently Used), LFU (Least Frequently Used), FIFO, TTL-based

### Cache Invalidation
- Hardest problem in CS; use versioned keys or TTL + event-driven invalidation

---

## Content Delivery Network (CDN)

- Geographically distributed proxy servers caching static content
- **Push CDN:** Upload new content to CDN on origin changes
- **Pull CDN:** CDN fetches from origin on first miss, then caches
- Best for: images, CSS, JS, video, software downloads

---

## DNS (Domain Name System)

- Hierarchical, distributed name → IP lookup
- **Records:** A, AAAA, CNAME, MX, NS, TXT
- **Resolution flow:** Browser → recursive resolver → root → TLD → authoritative
- TTL controls caching duration

---

## Databases: SQL vs NoSQL

### SQL (Relational)
- Structured schema, ACID transactions
- JOIN support, mature tooling
- Vertical scaling; read replicas for horizontal read scaling
- Good for: financial data, complex queries, strong consistency needs

### NoSQL
- **Key-Value:** Redis, DynamoDB (fast lookups)
- **Document:** MongoDB, CouchDB (flexible schema)
- **Column-Family:** Cassandra, HBase (time-series, wide-column)
- **Graph:** Neo4j, ArangoDB (relationship-heavy)
- Eventually consistent; horizontal scaling native
- Good for: high write throughput, flexible schema, massive scale

---

## CAP Theorem

- **C (Consistency):** Every read returns the most recent write
- **A (Availability):** Every request gets a response (non-error)
- **P (Partition Tolerance):** System continues despite network partitions
- Network partitions are inevitable → choose CP or AP
  - **CP:** HBase, MongoDB (consistency over availability)
  - **AP:** Cassandra, DynamoDB (availability over consistency)

---

## Consistent Hashing

- Map both servers and keys onto a hash ring
- Each key assigned to next server clockwise on ring
- Adding/removing a server only remaps ~1/N of keys
- Use virtual nodes to address non-uniform distribution

---

## Rate Limiting

### Algorithms
- **Token Bucket:** Tokens added at fixed rate; consume per request; handles bursts
- **Leaky Bucket:** Requests queue and process at fixed rate; smooths traffic
- **Fixed Window Counter:** Count requests per time window; simple but bursty at edges
- **Sliding Window Log:** Timestamped set; accurate but memory-heavy

### Implementation
- Redis-backed distributed counters
- Return HTTP 429 with `Retry-After` header
- Different limits per user tier, endpoint, or API key

---

## Microservices vs Monolith

### Monolith
- Single deployable unit; simple to develop and deploy initially
- Harder to scale independently; tight coupling over time

### Microservices
- Small, independent services with their own databases
- Scale, deploy, and develop independently
- **Tradeoffs:** Network latency, distributed transactions, operational complexity
- Use API gateway for routing, auth, rate limiting

### When to Choose What
- Start monolith; extract microservices when team size or scale demands it
- Domain-Driven Design helps define service boundaries

---

## Key Metrics (Back-of-Envelope)

| Metric | Typical Value |
|---|---|
| L1 cache reference | 0.5 ns |
| L2 cache reference | 7 ns |
| Main memory reference | 100 ns |
| SSD random read | 150 μs |
| HDD random read | 10 ms |
| Same-region network RTT | 0.5 ms |
| Cross-continent network RTT | 150 ms |

---

## High-Level Design Framework (for interviews)

1. **Requirements clarification:** functional + non-functional
2. **Back-of-envelope estimation:** QPS, storage, bandwidth
3. **High-level design:** major components, data flow
4. **Detailed design:** database schema, API design, deep dives
5. **Bottlenecks & tradeoffs:** identify and address
