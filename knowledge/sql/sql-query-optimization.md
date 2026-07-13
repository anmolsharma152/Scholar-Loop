---
difficulty: hard
last_sent:
review_count: 0
tags:
  - sql
  - optimization
topic: sql
---

# SQL Query Optimization

Query optimization is the difference between a 1ms response and a 10-second timeout. This covers index design, EXPLAIN ANALYZE interpretation, and common optimization patterns.

## Index Fundamentals

An index is a data structure that speeds up data retrieval at the cost of slower writes and more storage:

| Index Type | Structure | Best For | Limitation |
|------------|-----------|----------|------------|
| B-tree | Balanced tree | Range queries, equality, ordering | Not great for very high cardinality |
| Hash | Hash table | Equality comparisons only | No range queries |
| Bitmap | Bit arrays | Low-cardinality columns (gender, status) | Poor for high-cardinality |
| GIN | Inverted index | Full-text search, arrays, JSONB | Slower updates |
| GiST | Generalized search tree | Geometric, full-text, ranges | Complex setup |

### B-tree Index (Default)

```sql
-- Single column index
CREATE INDEX idx_employees_dept ON employees(department);

-- Composite index (order matters!)
CREATE INDEX idx_employees_dept_salary ON employees(department, salary);

-- Covering index (includes extra columns to avoid table lookup)
CREATE INDEX idx_employees_covering ON employees(department, salary) 
INCLUDE (name, email);

-- Unique index
CREATE UNIQUE INDEX idx_employees_email ON employees(email);

-- Partial index (index only matching rows)
CREATE INDEX idx_active_employees ON employees(department) 
WHERE status = 'active';
```

## Composite Index Order

The order of columns in a composite index determines which queries it can serve:

```sql
CREATE INDEX idx ON employees(department, salary, hire_date);

-- ✅ Uses index (leftmost prefix matched)
WHERE department = 'Engineering'
WHERE department = 'Engineering' AND salary > 100000
WHERE department = 'Engineering' AND salary > 100000 AND hire_date > '2020-01-01'

-- ❌ Cannot use index (skips department)
WHERE salary > 100000
WHERE salary > 100000 AND hire_date > '2020-01-01'

-- ⚠️ Partial use (department uses index, salary can't range efficiently)
WHERE department = 'Engineering' AND hire_date > '2020-01-01'
```

**Rule**: Equality columns first, range columns second, SELECT columns last (for covering indexes).

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

## Covering Indexes

A covering index includes all columns needed by the query, eliminating the table lookup:

```sql
-- Query
SELECT department, salary FROM employees WHERE department = 'Engineering';

-- Covering index (no table lookup needed)
CREATE INDEX idx_employees_covering ON employees(department, salary);

-- The query can be answered entirely from the index
-- This is often 10-100x faster than a non-covering index
```

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

**Normalization forms**:
- **1NF**: No repeating groups, atomic values
- **2NF**: No partial dependencies (all non-key columns depend on entire primary key)
- **3NF**: No transitive dependencies (non-key columns don't depend on other non-key columns)

### Strategic Denormalization

```sql
-- Instead of JOIN every time:
SELECT e.name, d.name as dept_name
FROM employees e JOIN departments d ON e.dept_id = d.id;

-- Denormalize: store department name directly
ALTER TABLE employees ADD COLUMN dept_name VARCHAR(100);
-- Now: SELECT name, dept_name FROM employees;
-- Trade-off: department name must be updated in both places
```

## Common Optimization Patterns

```sql
-- ❌ Bad: Function on indexed column prevents index use
WHERE YEAR(hire_date) = 2024
-- ✅ Good: Range query uses index
WHERE hire_date >= '2024-01-01' AND hire_date < '2025-01-01'

-- ❌ Bad: SELECT * fetches unnecessary columns
SELECT * FROM employees WHERE department = 'Eng';
-- ✅ Good: Select only needed columns
SELECT name, salary FROM employees WHERE department = 'Eng';

-- ❌ Bad: NOT IN with subquery (slow, NULL issues)
WHERE id NOT IN (SELECT emp_id FROM terminated);
-- ✅ Good: LEFT JOIN + IS NULL or NOT EXISTS
WHERE NOT EXISTS (SELECT 1 FROM terminated t WHERE t.emp_id = e.id);

-- ❌ Bad: LIKE '%prefix' prevents index use
WHERE name LIKE '%son';
-- ✅ Good: LIKE 'prefix%' can use index
WHERE name LIKE 'John%';

-- ❌ Bad: OR prevents index use
WHERE department = 'Eng' OR salary > 100000;
-- ✅ Good: UNION ALL (if indexed separately)
SELECT * FROM employees WHERE department = 'Eng'
UNION ALL
SELECT * FROM employees WHERE salary > 100000 AND department <> 'Eng';
```

## Key Takeaways

- EXPLAIN ANALYZE is your first tool for diagnosing slow queries
- Composite index order matters: equality first, range second, covering last
- Seq Scan on large tables almost always means a missing index
- ANALYZE your tables regularly to keep statistics fresh
- Covering indexes eliminate table lookups — massive performance gain
- Normalize for write-heavy, denormalize for read-heavy workloads
- Functions on columns in WHERE clauses prevent index usage
- Always benchmark: intuition about query performance is often wrong

## Common Bugs

| Bug | Symptom | Fix |
|-----|---------|-----|
| Stale statistics | Bad query plans, wrong estimates | Run `ANALYZE table_name` |
| Index not used (selectivity) | Seq Scan despite index | Check if index is selective enough (<15% rows) |
| Function on indexed column | Index ignored | Rewrite to avoid function in WHERE |
| Wrong composite index order | Index not used | Put equality columns first |
| Missing INCLUDE in covering index | Table lookup still happens | Add INCLUDE clause |
| Over-indexing | Slow writes, wasted space | Review unused indexes: `pg_stat_user_indexes` |
