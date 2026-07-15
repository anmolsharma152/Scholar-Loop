---
created: '2026-07-16'
difficulty: easy
tags:
- excel
- spreadsheet
- formulas
topic: fullstack
---

# Excel Fundamentals

Excel is a spreadsheet application for storing, analyzing, and visualizing data. Key concepts for data analyst interviews.

## Core Concepts

**Cell**: Intersection of a row and column. Address = column letter + row number (e.g., A1, B5).

**Workbook vs Worksheet**: A workbook contains multiple worksheets (tabs). Each worksheet is a grid of cells.

**Relative vs Absolute References**:
- Relative: `=A1+B1` — adjusts when copied (A2+B2 in next row)
- Absolute: `=$A$1+$B$1` — stays fixed when copied (use `$` to lock)
- Mixed: `=A$1+B1` — locks row only; `=$A1+B1` locks column only

## Essential Functions

**Summarization:**
```excel
=SUM(A1:A10)           # Sum of range
=SUMIF(A:A, ">100", B:B)  # Sum where condition met
=AVERAGE(B2:F2)        # Arithmetic mean
=COUNT(A:A)            # Count numeric cells
=COUNTA(A:A)           # Count non-empty cells
=COUNTBLANK(A:A)       # Count empty cells
=COUNTIF(A:A, ">50")   # Count matching condition
=COUNTIFS(A:A, ">50", B:B, "<100")  # Multiple conditions
```

**Lookup:**
```excel
=VLOOKUP(lookup_val, table, col_idx, FALSE)  # Vertical lookup
=HLOOKUP(lookup_val, table, row_idx, FALSE)  # Horizontal lookup
=MATCH(lookup_val, lookup_array, 0)          # Find position
=INDEX(range, row, col)                      # Get value by position
```

VLOOKUP searches the leftmost column, moves right to `col_idx`. Set `FALSE` for exact match, `TRUE` for approximate (data must be sorted ascending).

**Date/Time:**
```excel
=TODAY()                    # Current date
=NOW()                      # Current date + time
=DATEDIFF(start, end, "d")  # Days between
=YEAR(A1), MONTH(A1), DAY(A1)  # Extract parts
```

**Logical:**
```excel
=IF(condition, true_val, false_val)
=AND(cond1, cond2)
=OR(cond1, cond2)
```

**Financial:**
```excel
=FV(rate, nper, pmt, [pv])  # Future value (compound interest)
```

## Pivot Tables

Summarize large datasets without formulas. Requires:
1. First row = unique column headers
2. No blank rows or columns
3. One value per cell

**Create**: Select data → Insert → Pivot Table

**Structure**:
- **Rows**: Group by (e.g., department)
- **Columns**: Sub-group (e.g., quarter)
- **Values**: Aggregate (sum, count, average)
- **Filters**: Slice the data

**Tips**:
- Double-click any value to see underlying detail
- Use "Defer Layout Update" for complex rearrangements
- Change aggregation: Right-click value → Value Field Settings

## Data Validation and Drop-downs

```excel
# Create drop-down list
Data → Data Validation → List → Source: =A1:A10
```

## Freezing Panes

View → Freeze Panes: keeps headers visible while scrolling.

- Freeze Top Row: locks row 1
- Freeze First Column: locks column A
- Freeze Panes: locks everything above and left of selection

## What-If Analysis

- **Scenarios**: Test multiple input sets (up to 32 variables)
- **Goal Seek**: Find input needed for a desired output
- **Data Tables**: Test 1-2 variables with many values

## Key Takeaways

- `$` in cell references makes them absolute (don't change when copied)
- VLOOKUP requires the lookup column to be leftmost; use INDEX/MATCH for flexibility
- Pivot Tables are the fastest way to summarize without formulas
- COUNT counts numbers, COUNTA counts non-empty, COUNTBLANK counts empty
- Always check data types before analysis — numbers stored as strings break formulas
