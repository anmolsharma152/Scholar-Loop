---
created: '2026-07-16'
difficulty: easy
tags:
- tableau
- visualization
- business-intelligence
topic: fullstack
---

# Tableau Fundamentals

Tableau is a business intelligence tool for interactive data visualization and dashboarding. Connects to databases, spreadsheets, and cloud sources.

## Core Concepts

**Dimensions vs Measures**:
- Dimensions: categorical fields (name, region, date) — used for grouping
- Measures: numeric fields (sales, quantity, profit) — used for aggregation

**Discrete vs Continuous**:
- Discrete (blue): categorical, creates headers
- Continuous (green): numeric, creates axes

## File Types

| Extension | Description |
|-----------|-------------|
| `.twb` | Tableau Workbook (no data) |
| `.twbx` | Packaged Workbook (with data) |
| `.tde` / `.hyper` | Data Extracts (optimized for performance) |

## Connecting Data

Click "Connect" → choose source type:
- Excel, CSV, JSON
- SQL databases (PostgreSQL, MySQL)
- Cloud (Google Analytics, Snowflake)

## Chart Types

**Bar chart**: Dimension on Columns, Measure on Rows
**Line chart**: Time dimension on Columns, Measure on Rows
**Scatter plot**: Two Measures on Columns and Rows
**Heat map**: Two Dimensions with Measure as color
**Dual-axis**: Two Measures on same shelf → right-click → Dual Axis → Synchronize

## Calculated Fields

Right-click in Data pane → Create Calculated Field:

```tableau
// Conditional
IF [Sales] > 1000 THEN 'High' ELSE 'Low' END

// CASE statement
CASE [Region]
  WHEN 'North' THEN 'Zone A'
  WHEN 'South' THEN 'Zone B'
  ELSE 'Other'
END

// Date difference
DATEDIFF('day', [Start Date], [End Date])

// Ranking
RANK_UNIQUE([Sales])
```

## Dashboards

A dashboard is a collection of visualizations on one screen.

**Create**: Drag sheets onto dashboard workspace
**Interactivity**: Add filters, highlighters, parameter controls
**Layout**: Use containers (horizontal/vertical) for responsive design

## Filtering

| Filter Type | Scope | Use Case |
|-------------|-------|----------|
| Dimension filter | Single viz | Exclude specific categories |
| Measure filter | Single viz | Range of values |
| Context filter | Entire viz | Priority filter (applied first) |
| Data source filter | Entire workbook | Restrict loaded data |
| Extract filter | Extract only | Reduce extract size |

## Data Blending vs Joining

- **Join**: Combines tables at database level (same data source)
- **Blend**: Combines data at visualization level (different data sources)
- Use blend when tables have different granularities or come from different sources

## Story Points

Sequence of visualizations in a narrative format. Each story point is a snapshot of insights. Used for presentations.

## Parameters

Dynamic values that replace constants in calculations:

```tableau
// Create parameter: [Profit Threshold]
// Use in calculated field:
IF [Profit] > [Profit Threshold] THEN 'Above' ELSE 'Below' END
```

## Performance Tips

- Use extracts (`.hyper`) for large datasets
- Hide unused fields and measures
- Use context filters to reduce data early
- Limit quick filters on dashboards
- Use data source filters over worksheet filters

## Key Takeaways

- Dimensions (blue) group data; Measures (green) aggregate data
- Dual-axis charts let you compare two measures on different scales
- Data blending is for cross-source analysis; joins are for same-source
- Extracts improve performance by pre-aggregating data
- Calculated fields use IF/CASE for conditional logic, RANK for ranking
