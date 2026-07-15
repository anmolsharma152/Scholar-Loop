---
difficulty: medium
last_sent:
review_count: 0
tags:
  - sql
  - cte
  - recursive
topic: sql
---

# SQL CTEs & Recursive Queries

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
```

CTEs improve readability for complex queries vs nested subqueries which become hard to parse.

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

- CTEs make complex queries readable; use them to break down logic
- Recursive CTEs are powerful for tree/graph traversal — always add cycle/depth guards
- EXISTS generally outperforms IN for large datasets
- Modern SQL prefers CTEs over nested subqueries for maintainability

## Common Bugs

| Bug | Symptom | Fix |
|-----|---------|-----|
| Infinite recursion in CTE | Stack overflow / timeout | Add depth limit `AND depth < N` |
| Missing cycle detection | Infinite loops in recursive CTE | Track visited nodes with ARRAY |
| CROSS JOIN on large tables | Massive result set, OOM | Use INNER JOIN or add WHERE clause |
