---
difficulty: hard
last_sent:
review_count: 0
tags:
  - sql
  - indexes
topic: sql
---

# SQL Index Design

## Index Fundamentals

An index speeds up data retrieval at the cost of slower writes and more storage:

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

## Common Bugs

| Bug | Symptom | Fix |
|-----|---------|-----|
| Index not used (selectivity) | Seq Scan despite index | Check if index is selective enough (<15% rows) |
| Function on indexed column | Index ignored | Rewrite to avoid function in WHERE |
| Wrong composite index order | Index not used | Put equality columns first |
| Missing INCLUDE in covering index | Table lookup still happens | Add INCLUDE clause |
| Over-indexing | Slow writes, wasted space | Review unused indexes: `pg_stat_user_indexes` |
