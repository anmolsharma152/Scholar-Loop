---
difficulty: hard
last_sent:
review_count: 0
tags:
  - sql
  - optimization
  - explain
topic: sql
---

# SQL EXPLAIN ANALYZE & Optimization

## EXPLAIN ANALYZE

EXPLAIN ANALYZE shows the actual query plan and execution time:

```sql
EXPLAIN ANALYZE
SELECT e.name, d.name as department
FROM employees e
JOIN departments d ON e.dept_id = d.id
WHERE e.salary > 80000;
```

### Reading the Output

```
Nested Loop  (cost=0.00..1523.45 rows=1000 width=48) (actual time=0.01..12.34 rows=950 loops=1)
  ->  Seq Scan on employees e  (cost=0.00..1200.00 rows=10000 width=12) (actual time=0.00..8.00 rows=10000 loops=1)
        Filter: (salary > 80000)
        Rows Removed by Filter: 15000
  ->  Index Scan using idx_departments_id on departments d  (cost=0.04..0.32 rows=1 width=36) (actual time=0.00..0.00 rows=1 loops=10000)
Planning Time: 0.123 ms
Execution Time: 12.567 ms
```

| Metric | Meaning |
|--------|---------|
| `cost` | Estimated cost (startup..total) — arbitrary units |
| `actual time` | Real execution time in ms (startup..total) |
| `rows` | Estimated vs actual rows returned |
| `loops` | How many times the node was executed |
| `Seq Scan` | Full table scan — often a red flag |
| `Index Scan` | Using an index — usually good |
| `Filter` | Rows removed after scanning |
| `Rows Removed by Filter` | How many rows were discarded |

### Key Red Flags

1. **Seq Scan on large tables**: Missing index
2. **Actual rows >> estimated rows**: Statistics are stale
3. **Nested Loop with high loops count**: Should be Hash/Hash Join
4. **Sort node**: Missing index for ORDER BY

## Query Plan Types

| Join Type | When Used | Optimization |
|-----------|-----------|-------------|
| Nested Loop | Small inner table, indexed join column | Ensure inner table has index |
| Hash Join | Medium-large tables, no useful index | Build hash on smaller table |
| Merge Join | Both inputs sorted on join key | Add indexes on join columns |

## Slow Query Analysis Pattern

```sql
-- Step 1: Get the execution plan
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) SELECT ...;

-- Step 2: Identify the bottleneck node (highest cost/time)
-- Step 3: Check if it's a Seq Scan on large table → add index
-- Step 4: Check if estimates are wildly off → ANALYZE table
-- Step 5: Check if JOIN type is suboptimal → restructure query

-- Update table statistics
ANALYZE employees;

-- Check existing indexes
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'employees';
```

## Normalization vs Denormalization

| Approach | Pros | Cons | Use When |
|----------|------|------|----------|
| Normalized (3NF) | No redundancy, consistent writes | Many JOINs | Write-heavy, transactional |
| Denormalized | Fast reads, fewer JOINs | Redundancy, slow writes | Read-heavy, analytics |

**1NF**: Atomic values. **2NF**: No partial dependencies. **3NF**: No transitive dependencies.

## Common Optimization Patterns

```sql
-- Function on indexed column prevents index use
WHERE YEAR(hire_date) = 2024                    -- bad
WHERE hire_date >= '2024-01-01' AND hire_date < '2025-01-01'  -- good

-- SELECT * fetches unnecessary columns
SELECT * FROM employees WHERE dept = 'Eng';      -- bad
SELECT name, salary FROM employees WHERE dept = 'Eng';  -- good

-- NOT IN with subquery is slow
WHERE id NOT IN (SELECT emp_id FROM terminated);  -- bad
WHERE NOT EXISTS (SELECT 1 FROM terminated t WHERE t.emp_id = e.id);  -- good

-- LIKE '%prefix' prevents index use
WHERE name LIKE '%son';                          -- bad
WHERE name LIKE 'John%';                         -- good
```

## Common Bugs

| Bug | Symptom | Fix |
|-----|---------|-----|
| Stale statistics | Bad query plans, wrong estimates | Run `ANALYZE table_name` |
| Function on indexed column | Index ignored | Rewrite to avoid function in WHERE |
| Over-indexing | Slow writes, wasted space | Review unused indexes: `pg_stat_user_indexes` |
