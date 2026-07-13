---
difficulty: medium
last_sent:
review_count: 0
tags:
  - sql
  - joins
  - subqueries
topic: sql
---

# Advanced SQL: Joins, Subqueries, and CTEs

Beyond basic JOINs and simple subqueries, SQL offers powerful constructs for complex data relationships: self-joins, lateral joins, correlated subqueries, CTEs, and recursive queries. These are essential for real-world analytics and data transformation.

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

## Lateral Joins (PostgreSQL/MySQL 8+)

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
| Readability | More verbose | Cleaner for simple cases |
| Optimization | Semi-join (database can optimize) | May materialize full list |

```sql
-- These are equivalent but may have different performance
-- EXISTS version (generally preferred)
SELECT * FROM employees e
WHERE EXISTS (
    SELECT 1 FROM departments d WHERE d.id = e.dept_id
);

-- IN version
SELECT * FROM employees e
WHERE e.dept_id IN (
    SELECT id FROM departments
);
```

## Common Table Expressions (CTEs)

CTEs (WITH clause) create named temporary result sets for cleaner, more readable queries:

```sql
WITH department_stats AS (
    SELECT department, AVG(salary) as avg_salary, COUNT(*) as count
    FROM employees
    GROUP BY department
),
high_earners AS (
    SELECT name, salary, department
    FROM employees
    WHERE salary > 100000
)
SELECT h.name, h.salary, h.department, d.avg_salary
FROM high_earners h
JOIN department_stats d ON h.department = d.department;

-- CTEs improve readability for complex queries
-- vs nested subqueries which become hard to parse
```

## Recursive CTEs

Recursive CTEs traverse hierarchical data (org charts, tree structures, graph traversal):

```sql
-- Employee hierarchy (org chart)
WITH RECURSIVE org_chart AS (
    -- Base case: top-level managers
    SELECT id, name, manager_id, 1 as level, 
           name as path
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- Recursive case: find reports
    SELECT e.id, e.name, e.manager_id, oc.level + 1,
           oc.path || ' → ' || e.name
    FROM employees e
    JOIN org_chart oc ON e.manager_id = oc.id
)
SELECT * FROM org_chart ORDER BY path;

-- Result:
-- id | name    | level | path
-- 1  | Alice   | 1     | Alice
-- 2  | Bob     | 2     | Alice → Bob
-- 3  | Charlie | 3     | Alice → Bob → Charlie
-- 4  | Diana   | 2     | Alice → Diana
```

### Graph Traversal Example

```sql
-- Find all paths between two nodes
WITH RECURSIVE paths AS (
    SELECT source, target, 
           ARRAY[source, target] as path,
           1 as depth
    FROM edges
    WHERE source = 'A'
    
    UNION ALL
    
    SELECT p.source, e.target,
           p.path || e.target,
           p.depth + 1
    FROM paths p
    JOIN edges e ON p.target = e.source
    WHERE e.target <> ALL(p.path)  -- prevent cycles
      AND p.depth < 10             -- prevent infinite loops
)
SELECT * FROM paths WHERE target = 'F';
```

## Advanced Subquery Patterns

```sql
-- Lateral join equivalent with correlated subquery
SELECT a.id, b.max_val
FROM table_a a
CROSS JOIN LATERAL (
    SELECT MAX(value) as max_val 
    FROM table_b b 
    WHERE b.group_id = a.id
) b;

-- Scalar subquery in SELECT (one value per row)
SELECT name, salary,
    salary - (SELECT AVG(salary) FROM employees) as diff_from_overall_avg
FROM employees;

-- Subquery in FROM (derived table)
SELECT dept, avg_salary
FROM (
    SELECT department as dept, AVG(salary) as avg_salary
    FROM employees
    GROUP BY department
) dept_avg
WHERE avg_salary > 80000;
```

## Key Takeaways

- Self-joins are essential for hierarchical and pair-finding queries
- LATERAL joins are the most efficient way to do "top-N per group"
- Correlated subqueries evaluate per outer row — can be slow without proper indexes
- CTEs make complex queries readable; use them to break down logic
- Recursive CTEs are powerful for tree/graph traversal — always add cycle/depth guards
- EXISTS generally outperforms IN for large datasets
- Modern SQL prefers CTEs over nested subqueries for maintainability

## Common Bugs

| Bug | Symptom | Fix |
|-----|---------|-----|
| Infinite recursion in CTE | Stack overflow / timeout | Add depth limit `AND depth < N` |
| Missing cycle detection | Infinite loops in recursive CTE | Track visited nodes with ARRAY |
| Correlated subquery without index | Very slow queries | Index correlated columns |
| CROSS JOIN on large tables | Massive result set, OOM | Use INNER JOIN or add WHERE clause |
| LATERAL without proper ordering | Wrong "top-N" results | Ensure ORDER BY in lateral subquery |
| Using IN with NULL values | Unexpected empty results | Use EXISTS or add `IS NOT NULL` |
