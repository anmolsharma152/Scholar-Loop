---
difficulty: medium
last_sent:
review_count: 0
tags:
  - sql
  - window-functions
topic: sql
---

# SQL Window Functions

Window functions perform calculations across a set of rows related to the current row — without collapsing them like GROUP BY. They are essential for ranking, running totals, moving averages, and row-to-row comparisons.

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

## Running Totals and Moving Averages

The frame clause controls which rows the function considers:

| Frame Type | Syntax | Rows Included |
|------------|--------|---------------|
| ROWS | `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` | All rows up to current |
| RANGE | `RANGE BETWEEN ...` | Logical range (same values) |
| GROUPS | `GROUPS BETWEEN ...` | Groups of peer rows |

```sql
SELECT 
    order_date, amount,
    -- Running total
    SUM(amount) OVER (ORDER BY order_date 
                      ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as running_total,
    -- 7-day moving average
    AVG(amount) OVER (ORDER BY order_date 
                      ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as moving_avg_7d,
    -- 3-row rolling sum
    SUM(amount) OVER (ORDER BY order_date 
                      ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING) as rolling_3
FROM orders;
```

### Frame Clause Diagram

```
UNBOUNDED PRECEDING ← [  row  row  row  ] → UNBOUNDED FOLLOWING
                              ↑
                          CURRENT ROW

ROWS BETWEEN 2 PRECEDING AND 1 FOLLOWING = [row, row, CURRENT, row]
```

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

## Window Functions vs Subqueries

Window functions are often cleaner and more efficient than equivalent subqueries:

```sql
-- Subquery approach (slower, more verbose)
SELECT e.name, e.salary, sub.dept_avg
FROM employees e
JOIN (
    SELECT department, AVG(salary) as dept_avg
    FROM employees GROUP BY department
) sub ON e.department = sub.department;

-- Window function approach (cleaner, faster)
SELECT name, salary,
    AVG(salary) OVER (PARTITION BY department) as dept_avg
FROM employees;
```

## Common Window Function Patterns

| Pattern | Use Case |
|---------|----------|
| `ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_at DESC)` | Get latest record per entity |
| `RANK() OVER (PARTITION BY dept ORDER BY salary DESC)` | Find top-N per group |
| `LAG(col) OVER (ORDER BY date)` | Compare with previous period |
| `SUM(col) OVER (ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)` | Running total |
| `COUNT(*) OVER ()` | Total count without collapsing |
| `FIRST_VALUE(col) OVER (ORDER BY date)` | Get first value per partition |

## Key Takeaways

- Window functions compute over a "window" of rows without collapsing results
- PARTITION BY groups data; ORDER BY sorts within partitions
- Ranking functions (ROW_NUMBER, RANK, DENSE_RANK) differ in gap handling
- LAG/LEAD access neighboring rows; frame clauses control the window scope
- Window functions are evaluated after WHERE but before ORDER BY
- Use window functions over subqueries for cleaner, faster SQL
- Multiple window functions can share the same OVER clause

## Common Bugs

| Bug | Symptom | Fix |
|-----|---------|-----|
| Missing ORDER BY in ranking | Non-deterministic order | Always specify ORDER BY for rankings |
| Using ROW_NUMBER with ties | Different results on rerun | Use RANK or DENSE_RANK if ties matter |
| Wrong frame clause default | Unexpected moving averages | Explicitly specify frame clause |
| Using window function in WHERE | Error | Wrap in subquery: `SELECT * FROM (subquery) WHERE ...` |
| PARTITION BY without ORDER BY | All rows in same frame | Add ORDER BY or use explicit frame |
| Confusing RANK with DENSE_RANK | Gaps in numbering | Use DENSE_RANK for gapless sequences |
