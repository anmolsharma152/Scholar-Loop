---
difficulty: medium
last_sent:
review_count: 0
tags:
  - sql
  - window-functions
  - frames
topic: sql
---

# SQL Window Functions: Frames & Running Calculations

## Frame Clauses

The frame clause controls which rows the function considers:

| Frame Type | Syntax | Rows Included |
|------------|--------|---------------|
| ROWS | `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` | All rows up to current |
| RANGE | `RANGE BETWEEN ...` | Logical range (same values) |
| GROUPS | `GROUPS BETWEEN ...` | Groups of peer rows |

```
UNBOUNDED PRECEDING ← [  row  row  row  ] → UNBOUNDED FOLLOWING
                              ↑
                          CURRENT ROW

ROWS BETWEEN 2 PRECEDING AND 1 FOLLOWING = [row, row, CURRENT, row]
```

## Running Totals and Moving Averages

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
- LAG/LEAD access neighboring rows; frame clauses control the window scope
- Window functions are evaluated after WHERE but before ORDER BY
- Use window functions over subqueries for cleaner, faster SQL
- Multiple window functions can share the same OVER clause

## Common Bugs

| Bug | Symptom | Fix |
|-----|---------|-----|
| Wrong frame clause default | Unexpected moving averages | Explicitly specify frame clause |
| PARTITION BY without ORDER BY | All rows in same frame | Add ORDER BY or use explicit frame |
| Using window function in WHERE | Error | Wrap in subquery: `SELECT * FROM (subquery) WHERE ...` |
