---
difficulty: medium
last_sent: null
review_count: 0
tags:
- caching
- performance
- redis
- memcached
topic: system-design
---

# Caching strategies

Caching stores frequently accessed data in fast storage (RAM) to reduce latency and database load. Think of it as keeping your most-used items on your desk instead of walking to the storage room every time.

## Patterns

1. **Cache-Aside (Lazy Loading)** — Application checks cache first. On miss, fetch from DB, then store in cache. Most common pattern. Simple but has a brief window of inconsistency after writes.
2. **Write-Through** — Data written to cache AND database simultaneously. Ensures consistency but slower writes since both must complete.
3. **Write-Back (Write-Behind)** — Data written to cache first, then asynchronously to database. Fast writes but risk of data loss on cache failure — good for analytics/metrics where some loss is acceptable.
4. **Read-Through** — Cache automatically loads data from database on miss. Application only talks to cache — cleaner code but less control.
5. **Write-Around** — Data written directly to database, bypassing cache. Cache only fills on reads. Good for write-heavy workloads where cached data is rarely read soon after write.

## Cache layers

```
Browser cache (static assets, 1-24h TTL)
  → CDN (global content delivery, 1h-7d TTL)
    → Application cache (Redis / Memcached, seconds-minutes TTL)
      → Database cache (query results, buffer pool)
```

Each layer has different TTLs and invalidation strategies. Browser cache is cheapest; database cache is fastest.

## Why use it

- Reduces database load by 80-90% — most reads never hit DB
- Improves response time from seconds to milliseconds — RAM vs disk
- Handles traffic spikes without scaling databases — cache absorbs read load
- Lowers infrastructure cost by deferring DB scaling — cache is cheaper than more DB replicas

## Trade-offs to remember

- **Cache invalidation is one of the hardest problems in CS** — Stale data happens. Design for it.
- **Cache stampede** — When many requests miss simultaneously (e.g., after TTL expires), they all hit DB at once. Use probabilistic early recomputation or locks.
- **Memory cost** — Caches are RAM, RAM is expensive. Cache hot data only.
- **Consistency** — Async patterns mean brief windows where cache and DB differ

## Choosing a pattern

Use **Cache-Aside** for most cases — simple, battle-tested. Use **Write-Through** when consistency is critical (financial data). Use **Write-Back** for high-write workloads where some loss is acceptable (analytics). Use **Write-Around** when writes vastly outnumber reads.

## Popular tools

Redis (most popular, rich data structures), Memcached (simple key-value, multi-threaded), Varnish (HTTP cache), Hazelcast (distributed cache)