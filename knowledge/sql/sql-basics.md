---
difficulty: easy
last_sent:
review_count: 0
tags:
  - sql
  - basics
topic: sql
---

# SQL Fundamentals

SQL (Structured Query Language) is the standard language for querying and manipulating relational databases. Mastering the basics — SELECT, JOINs, GROUP BY, and NULL handling — is essential for any data professional.

## SELECT and Filtering

The most fundamental SQL operation retrieves data from tables with optional filtering:

```sql
-- Basic SELECT
SELECT column1, column2 FROM table_name;

-- Select all columns
SELECT * FROM employees;

-- Filter with WHERE
SELECT name, salary 
FROM employees 
WHERE department = 'Engineering' AND salary > 80000;

-- Pattern matching
SELECT name FROM employees WHERE name LIKE '%son%';

-- Range filtering
SELECT name, salary FROM employees 
WHERE salary BETWEEN 50000 AND 100000;

-- Sorting and limiting
SELECT name, salary FROM employees 
ORDER BY salary DESC 
LIMIT 10;
```

## JOIN Operations

JOINs combine rows from two or more tables based on related columns:

| JOIN Type | Returns |
|-----------|---------|
| INNER JOIN | Only matching rows from both tables |
| LEFT JOIN | All rows from left + matching from right (NULLs if no match) |
| RIGHT JOIN | All rows from right + matching from left |
| FULL OUTER JOIN | All rows from both tables (NULLs where no match) |

```sql
-- INNER JOIN: only employees with departments
SELECT e.name, d.department_name
FROM employees e
INNER JOIN departments d ON e.dept_id = d.id;

-- LEFT JOIN: all employees, even without department
SELECT e.name, d.department_name
FROM employees e
LEFT JOIN departments d ON e.dept_id = d.id;

-- FULL OUTER JOIN: all employees and all departments
SELECT e.name, d.department_name
FROM employees e
FULL OUTER JOIN departments d ON e.dept_id = d.id;
```

### Visual Comparison

```
Table A:  [1, 2, 3]    Table B:  [2, 3, 4]

INNER:        [2, 3]
LEFT:    [1, 2, 3]
RIGHT:           [2, 3, 4]
FULL:     [1, 2, 3, 4]
```

## GROUP BY and Aggregation

GROUP BY collapses rows into groups and applies aggregate functions:

| Aggregate | Description | NULL Handling |
|-----------|-------------|---------------|
| COUNT(*) | Number of rows | Counts NULLs |
| COUNT(col) | Non-NULL values in column | Ignores NULLs |
| SUM(col) | Sum of values | Ignores NULLs |
| AVG(col) | Average of values | Ignores NULLs |
| MIN/MAX | Smallest/largest | Ignores NULLs |

```sql
-- Count employees per department
SELECT department, COUNT(*) as emp_count
FROM employees
GROUP BY department
ORDER BY emp_count DESC;

-- Average salary by department, only show groups with > 5 employees
SELECT department, AVG(salary) as avg_salary, COUNT(*) as count
FROM employees
GROUP BY department
HAVING COUNT(*) > 5;
```

**WHERE vs HAVING**: WHERE filters rows before grouping; HAVING filters groups after aggregation.

```sql
-- WHERE filters rows, then GROUP BY aggregates
SELECT department, AVG(salary)
FROM employees
WHERE status = 'active'      -- filters before grouping
GROUP BY department
HAVING AVG(salary) > 75000;  -- filters after grouping
```

## ORDER BY

Sorts results by one or more columns:

```sql
SELECT name, salary, department
FROM employees
ORDER BY department ASC, salary DESC;

-- Sort by column position
SELECT name, salary FROM employees ORDER BY 2 DESC;

-- Sort by expression
SELECT name, salary FROM employees ORDER BY salary * 1.1 DESC;

-- NULL ordering
SELECT name, commission FROM employees 
ORDER BY commission DESC NULLS LAST;
```

## LIMIT and OFFSET

Restricts the number of returned rows — essential for pagination:

```sql
-- First 10 results
SELECT * FROM employees ORDER BY id LIMIT 10;

-- Page 2 (offset 10, next 10)
SELECT * FROM employees ORDER BY id LIMIT 10 OFFSET 10;

-- SQL Server syntax
SELECT * FROM employees ORDER BY id 
OFFSET 10 ROWS FETCH NEXT 10 ROWS ONLY;
```

## NULL Handling

NULL represents missing or unknown data. NULL has special behavior:

```sql
-- NULL comparisons return NULL (not TRUE or FALSE)
SELECT * FROM employees WHERE commission = NULL;   -- WRONG: returns nothing
SELECT * FROM employees WHERE commission IS NULL;  -- CORRECT

-- COALESCE: return first non-NULL value
SELECT name, COALESCE(commission, 0) as commission
FROM employees;

-- NULLIF: returns NULL if arguments are equal
SELECT salary / NULLIF(headcount, 0) as salary_per_person
FROM departments;

-- ISNULL (SQL Server) / IFNULL (MySQL)
SELECT name, IFNULL(commission, 0) as commission FROM employees;
```

### NULL in Aggregations

```sql
SELECT 
    COUNT(*) as total_rows,
    COUNT(commission) as non_null_commissions,  -- excludes NULLs
    AVG(commission) as avg_commission            -- excludes NULLs from average
FROM employees;
```

## Common SQL Functions

| Category | Functions |
|----------|-----------|
| String | CONCAT, SUBSTRING, LENGTH, UPPER, LOWER, TRIM, REPLACE |
| Date | NOW, DATEADD, DATEDIFF, EXTRACT, DATE_FORMAT |
| Numeric | ROUND, CEIL, FLOOR, ABS, MOD |
| Conditional | CASE WHEN, COALESCE, NULLIF, IIF |

```sql
SELECT 
    UPPER(name) as name_upper,
    LENGTH(name) as name_len,
    ROUND(salary / 1000, 1) as salary_k,
    CASE 
        WHEN salary > 100000 THEN 'Senior'
        WHEN salary > 60000 THEN 'Mid'
        ELSE 'Junior'
    END as level
FROM employees;
```

## Key Takeaways

- Always use explicit JOIN syntax rather than comma-separated tables
- WHERE filters before grouping; HAVING filters after
- NULL requires special handling — use `IS NULL`, not `= NULL`
- COALESCE is the portable way to handle NULL defaults
- ORDER BY can reference column aliases and expressions
- Use LIMIT/OFFSET for pagination (syntax varies by database)
- Learn your database's specific NULL ordering defaults

## Common Bugs

| Bug | Symptom | Fix |
|-----|---------|-----|
| `= NULL` instead of `IS NULL` | Returns empty result | Use `IS NULL` |
| Missing GROUP BY in SELECT with aggregates | Error (PostgreSQL) or random values (MySQL) | Group by all non-aggregated columns |
| Using WHERE instead of HAVING | Can't filter on aggregates | Use HAVING for aggregate conditions |
| SELECT * in production code | Unexpected columns, poor performance | Specify explicit column list |
| Not aliasing ambiguous columns | "Column ambiguous" error | Use table aliases |
| COUNT(DISTINCT) on NULL | NULLs ignored | Use COALESCE if NULLs should be counted |
