---
created: '2026-07-16'
difficulty: medium
tags:
- sql
- case-study
- interview
topic: sql
---

# SQL Case Study Framework

A structured approach to solving open-ended SQL case study questions in data analyst interviews.

## The Problem

Unlike standard SQL questions ("write a query that returns X"), case studies give you a business scenario: "Unsubscribe rates are rising. Investigate." You must define metrics, write queries, and draw conclusions — all in 30-60 minutes.

## Step 1: Ask Clarifying Questions

Before writing any code, ask:

- **Data quality**: Are there duplicates? Missing values? Outliers?
- **Assumptions**: What should I assume about the data? (e.g., "all users are in the A/B test")
- **Scope**: What time period matters? Which segments?
- **Definition**: How is "unsubscribe" defined? What counts as "active"?

Write your assumptions on the board. Interviewers reward explicit reasoning.

## Step 2: Define the Metric

Translate the business question into measurable SQL concepts.

| Business Question | SQL Metric |
|---|---|
| "Are unsubscribes rising?" | COUNT of unsubscribe events / total users per week |
| "Which channel drives churn?" | Churn rate GROUP BY acquisition channel |
| "Is the A/B test working?" | Conversion rate difference with confidence interval |

## Step 3: Break Into Sub-Queries

Most case studies need 2-3 queries chained together:

1. **Isolate the cohort** — filter to relevant users/events
2. **Compute the metric** — aggregate, group by time/segment
3. **Compare segments** — join control vs. variant, before vs. after

**Example: Unsubscribe impact on login rates**
```sql
-- Step 1: Find all unsubscribers with their A/B bucket
WITH unsubscribers AS (
  SELECT user_id, MIN(event_date) AS unsub_date
  FROM events
  WHERE action = 'unsubscribe'
  GROUP BY user_id
),
-- Step 2: Compute login rates relative to unsubscribe date
login_rates AS (
  SELECT
    v.variant,
    DATEDIFF(e.event_date, u.unsub_date) AS days_from_unsub,
    AVG(CASE WHEN e.action = 'login' THEN 1.0 ELSE 0.0 END) AS login_rate
  FROM events e
  JOIN unsubscribers u ON e.user_id = u.user_id
  JOIN variants v ON e.user_id = v.user_id
  WHERE DATEDIFF(e.event_date, u.unsub_date) BETWEEN -30 AND 30
  GROUP BY v.variant, days_from_unsub
)
SELECT * FROM login_rates ORDER BY variant, days_from_unsub;
```

## Step 4: Analyze and Conclude

- State what the data shows (not just what the query returns)
- Call out limitations (small sample size, confounding variables)
- Suggest next steps (deeper segmentation, longer time window)

## Common Patterns

**A/B test analysis:**
```sql
SELECT variant,
  COUNT(*) AS users,
  AVG(CASE WHEN converted THEN 1.0 ELSE 0.0 END) AS conversion_rate
FROM users GROUP BY variant;
```

**Trend detection:**
```sql
SELECT DATE_TRUNC('week', created_at) AS week,
  COUNT(*) AS events,
  LAG(COUNT(*)) OVER (ORDER BY DATE_TRUNC('week', created_at)) AS prev_week
FROM events GROUP BY 1;
```

**Funnel analysis:**
```sql
SELECT
  COUNT(*) FILTER (WHERE step = 'view') AS views,
  COUNT(*) FILTER (WHERE step = 'click') AS clicks,
  COUNT(*) FILTER (WHERE step = 'purchase') AS purchases
FROM funnel_events;
```

## Key Takeaways

- Spend 5 minutes planning before writing any SQL
- Always state your assumptions explicitly
- Build queries incrementally — each CTE should be testable alone
- The conclusion matters as much as the query
- Practice with real case studies, not just syntax
