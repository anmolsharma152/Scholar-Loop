---
created: '2026-07-16'
difficulty: medium
tags:
- sql
- interview
- patterns
topic: sql
---

# SQL Interview Query Patterns

Common SQL patterns that appear repeatedly in technical interviews. Master these and you can handle most screening questions.

## Filtering Patterns

**Multiple conditions with IN:**
```sql
SELECT name FROM employees
WHERE department IN ('Engineering', 'Data', 'Product');
```

**Pattern matching with LIKE:**
```sql
-- % matches zero or more characters
SELECT * FROM users WHERE email LIKE '%@gmail.com';
-- _ matches exactly one character
SELECT * FROM products WHERE sku LIKE 'PRD_2024';
```

**Checking for NULL:**
```sql
SELECT COUNT(*) FROM orders WHERE shipped_at IS NULL;
SELECT * FROM users WHERE deleted_at IS NOT NULL;
```

**Range queries with BETWEEN (inclusive):**
```sql
SELECT title FROM films
WHERE release_year BETWEEN 2020 AND 2024;
```

## Aggregation Patterns

**Counting with GROUP BY:**
```sql
SELECT department, COUNT(*) as headcount
FROM employees
GROUP BY department
HAVING COUNT(*) > 5;
```

**Finding duplicates:**
```sql
SELECT email, COUNT(*) as cnt
FROM users
GROUP BY email
HAVING COUNT(*) > 1;
```

**Difference between total and distinct:**
```sql
SELECT COUNT(city) - COUNT(DISTINCT city) AS duplicates
FROM station;
```

**Conditional aggregation:**
```sql
SELECT
  COUNT(*) FILTER (WHERE status = 'active') AS active_count,
  COUNT(*) FILTER (WHERE status = 'churned') AS churned_count
FROM subscriptions;
```

## Join Patterns

**Left join to find missing records:**
```sql
-- Users who never placed an order
SELECT u.name
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.id IS NULL;
```

**Self join for comparisons:**
```sql
-- Employees earning more than their manager
SELECT e.name
FROM employees e
JOIN managers m ON e.manager_id = m.id
WHERE e.salary > m.salary;
```

**Join with aggregation:**
```sql
SELECT c.name, COUNT(o.id) AS order_count
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.name
ORDER BY order_count DESC;
```

## Ranking Patterns

**Top N per group:**
```sql
SELECT * FROM (
  SELECT name, salary, department,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS rn
  FROM employees
) sub
WHERE rn <= 3;
```

**Dense rank for distinct rankings:**
```sql
SELECT name, salary,
  DENSE_RANK() OVER (ORDER BY salary DESC) AS rank
FROM employees;
```

**Difference between ROW_NUMBER, RANK, DENSE_RANK:**
- ROW_NUMBER: sequential 1,2,3,4 (no ties)
- RANK: 1,2,2,4 (gaps after ties)
- DENSE_RANK: 1,2,2,3 (no gaps)

## String Patterns

**Extracting substrings:**
```sql
SELECT
  LEFT(name, POSITION(' ' IN name) - 1) AS first_name,
  SUBSTRING(name FROM POSITION(' ' IN name) + 1) AS last_name
FROM users;
```

**Cleaning data:**
```sql
SELECT
  REPLACE(ssn, '-', '') AS clean_ssn,
  TRIM(UPPER(email)) AS normalized_email
FROM contacts;
```

## Date Patterns

**Filtering by date range:**
```sql
SELECT * FROM orders
WHERE created_at >= '2024-01-01'
  AND created_at < '2025-01-01';
```

**Extracting date parts:**
```sql
SELECT
  EXTRACT(YEAR FROM created_at) AS year,
  EXTRACT(MONTH FROM created_at) AS month,
  COUNT(*) AS order_count
FROM orders
GROUP BY 1, 2
ORDER BY 1, 2;
```

## Key Takeaways

- IN is cleaner than multiple OR conditions
- Always use IS NULL / IS NOT NULL, never = NULL
- HAVING filters after aggregation, WHERE filters before
- LEFT JOIN ... WHERE right.id IS NULL finds missing records
- ROW_NUMBER vs RANK vs DENSE_RANK: know when gaps matter
- Integer division truncates — use 4.0/3.0 not 4/3
