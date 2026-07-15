---
difficulty: medium
last_sent:
review_count: 0
tags:
  - sql
  - joins
  - lateral
topic: sql
---

# SQL Self-Joins, Cross Joins & LATERAL

## Self-Joins

A self-join joins a table with itself — useful for hierarchical data, comparing rows, or finding pairs.

```sql
-- Find employees and their managers
SELECT 
    e.name as employee, 
    m.name as manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;

-- Find employees with same salary as another employee
SELECT DISTINCT 
    a.name as employee1, 
    b.name as employee2, 
    a.salary
FROM employees a
JOIN employees b ON a.salary = b.salary AND a.id < b.id;

-- Find consecutive days (self-join approach)
SELECT a.date, a.amount
FROM orders a
JOIN orders b ON b.date = a.date + INTERVAL '1 day'
WHERE a.amount > 1000;
```

## Cross Joins

Produces the Cartesian product — every row from A paired with every row from B:

```sql
-- All combinations of products and colors
SELECT p.product_name, c.color_name
FROM products p
CROSS JOIN colors c;

-- Generate date series (useful for filling gaps)
SELECT d.date, COALESCE(s.total, 0) as sales
FROM (
    SELECT generate_series('2024-01-01'::date, '2024-01-31'::date, '1 day') as date
) d
LEFT JOIN daily_sales s ON d.date = s.date;
```

**Warning**: Cross joins on large tables produce massive result sets (A × B rows).

## LATERAL Joins (PostgreSQL/MySQL 8+)

A LATERAL join allows a subquery to reference columns from preceding tables — the subquery is evaluated once per row:

```sql
-- Top 3 salaries per department
SELECT d.name as department, top_sal.*
FROM departments d
CROSS JOIN LATERAL (
    SELECT name, salary
    FROM employees e
    WHERE e.department_id = d.id
    ORDER BY salary DESC
    LIMIT 3
) top_sal;

-- Find nearest store for each customer
SELECT c.name, nearest.*
FROM customers c
CROSS JOIN LATERAL (
    SELECT store_name, 
           ST_Distance(c.location, s.location) as distance
    FROM stores s
    ORDER BY c.location <-> s.location
    LIMIT 1
) nearest;
```

Without LATERAL, you'd need window functions + subqueries. LATERAL is more efficient for "top-N per group" patterns.

## Correlated Subqueries

A subquery that references the outer query — evaluated once per outer row:

```sql
-- Employees earning more than their department average
SELECT name, salary, department
FROM employees e1
WHERE salary > (
    SELECT AVG(salary)
    FROM employees e2
    WHERE e2.department = e1.department  -- correlates with outer query
);

-- EXISTS: check if related rows exist
SELECT d.name
FROM departments d
WHERE EXISTS (
    SELECT 1 FROM employees e 
    WHERE e.department_id = d.id 
    AND e.salary > 100000
);

-- NOT EXISTS: find departments with no high earners
SELECT d.name
FROM departments d
WHERE NOT EXISTS (
    SELECT 1 FROM employees e 
    WHERE e.department_id = d.id 
    AND e.salary > 100000
);
```

### EXISTS vs IN

| Aspect | EXISTS | IN |
|--------|--------|-----|
| Performance | Better on large outer, small subquery | Better on small outer, indexed subquery |
| NULL handling | Handles NULLs correctly | `NULL IN (NULL)` returns NULL, not TRUE |
| Optimization | Semi-join (database can optimize) | May materialize full list |

## Common Bugs

| Bug | Symptom | Fix |
|-----|---------|-----|
| Correlated subquery without index | Very slow queries | Index correlated columns |
| CROSS JOIN on large tables | Massive result set, OOM | Use INNER JOIN or add WHERE clause |
| LATERAL without proper ordering | Wrong "top-N" results | Ensure ORDER BY in lateral subquery |
| Using IN with NULL values | Unexpected empty results | Use EXISTS or add `IS NOT NULL` |
