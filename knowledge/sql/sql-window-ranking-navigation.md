---
difficulty: medium
last_sent:
review_count: 0
tags:
  - sql
  - window-functions
  - ranking
topic: sql
---

# SQL Window Functions: Ranking & Navigation

## Window Function Syntax

```sql
function_name(args) OVER (
    [PARTITION BY partition_expression]
    [ORDER BY sort_expression [ASC|DESC]]
    [frame_clause]
)
```

- **PARTITION BY**: Divides rows into groups (like GROUP BY but keeps all rows)
- **ORDER BY**: Determines the order within each partition
- **Frame clause**: Defines which rows in the partition are included

## Ranking Functions

| Function | Behavior | Gaps |
|----------|----------|------|
| ROW_NUMBER() | Unique sequential number per row | No gaps |
| RANK() | Ties get same rank | Gaps after ties |
| DENSE_RANK() | Ties get same rank | No gaps |

```sql
SELECT 
    name, department, salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) as row_num,
    RANK()       OVER (ORDER BY salary DESC) as rank_val,
    DENSE_RANK() OVER (ORDER BY salary DESC) as dense_rank_val
FROM employees;

-- Result:
-- name    | dept    | salary | row_num | rank | dense_rank
-- Alice   | Eng     | 120000 | 1       | 1    | 1
-- Bob     | Eng     | 110000 | 2       | 2    | 2
-- Charlie | Sales   | 110000 | 3       | 2    | 2  ← tie
-- Diana   | Sales   | 100000 | 4       | 4    | 3  ← rank skips, dense doesn't
```

### Per-Department Ranking

```sql
SELECT name, department, salary,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) as dept_rank
FROM employees;

-- Result:
-- name    | dept    | salary | dept_rank
-- Alice   | Eng     | 120000 | 1
-- Bob     | Eng     | 110000 | 2
-- Charlie | Sales   | 110000 | 1  ← rank resets per department
-- Diana   | Sales   | 100000 | 2
```

## LAG and LEAD

Access values from previous or next rows:

```sql
SELECT 
    name, hire_date, salary,
    LAG(salary, 1)  OVER (ORDER BY hire_date) as prev_salary,
    LEAD(salary, 1) OVER (ORDER BY hire_date) as next_salary,
    salary - LAG(salary, 1) OVER (ORDER BY hire_date) as salary_change
FROM employees;

-- Result:
-- name    | hire_date | salary | prev_salary | next_salary | change
-- Alice   | 2020-01   | 100000 | NULL        | 110000      | NULL
-- Bob     | 2021-03   | 110000 | 100000      | 120000      | 10000
-- Charlie | 2022-06   | 120000 | 110000      | NULL        | 10000
```

Default offset is 1. LAG/LEAD can accept a default value: `LAG(salary, 1, 0)`.

## NTILE

Divides rows into equal buckets:

```sql
SELECT name, salary,
    NTILE(4) OVER (ORDER BY salary DESC) as quartile
FROM employees;

-- 4 employees → each gets one row per quartile
-- 5 employees → quartiles 1-2 get 2 rows, 3-4 get 1 row
```

Useful for percentile calculations and data distribution analysis.

## PARTITION BY vs GROUP BY

| Aspect | GROUP BY | PARTITION BY |
|--------|----------|-------------|
| Rows returned | Collapsed (one per group) | All rows preserved |
| Non-aggregated columns | Must be in GROUP BY | Can be selected freely |
| Use case | Summary statistics | Per-row calculations within groups |
| Output rows | Fewer than input | Same as input |

```sql
-- GROUP BY: collapses to one row per department
SELECT department, AVG(salary) as avg_salary
FROM employees
GROUP BY department;

-- PARTITION BY: keeps all rows, adds department average as new column
SELECT name, department, salary,
    AVG(salary) OVER (PARTITION BY department) as dept_avg_salary,
    salary - AVG(salary) OVER (PARTITION BY department) as diff_from_avg
FROM employees;
```

## Common Bugs

| Bug | Symptom | Fix |
|-----|---------|-----|
| Missing ORDER BY in ranking | Non-deterministic order | Always specify ORDER BY for rankings |
| Using ROW_NUMBER with ties | Different results on rerun | Use RANK or DENSE_RANK if ties matter |
| Using window function in WHERE | Error | Wrap in subquery: `SELECT * FROM (subquery) WHERE ...` |
| Confusing RANK with DENSE_RANK | Gaps in numbering | Use DENSE_RANK for gapless sequences |
