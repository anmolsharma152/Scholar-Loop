---
created: '2026-07-16'
difficulty: medium
tags:
- python
- pandas
- data-analysis
topic: fullstack
---

# Pandas Fundamentals

Pandas is the workhorse of data analysis in Python. Built on NumPy, it adds labeled axes and heterogeneous column types via DataFrames.

## Inspecting Data

```python
import pandas as pd

df.head()           # First 5 rows
df.info()           # Column names, types, non-null counts
df.shape            # (rows, columns)
df.describe()       # Summary stats for numeric columns
df.dtypes           # Data types per column
df.columns          # Column names (Index object)
df.values           # Underlying NumPy array
```

## Subsetting

**Columns:**
```python
df['name']               # Single column (Series)
df[['name', 'age']]      # Multiple columns (DataFrame)
```

**Rows with conditions:**
```python
df[df['age'] > 30]                              # Single condition
df[(df['age'] > 30) & (df['city'] == 'NYC')]    # Multiple (&, |, ~)
df[df['color'].isin(['red', 'blue'])]            # Membership
```

**Rows with dates:**
```python
df[df['date'] > '2024-01-01']
```

## Sorting

```python
df.sort_values('age')                    # Ascending
df.sort_values('age', ascending=False)   # Descending
df.sort_values(['city', 'age'])          # Multiple columns
```

## Adding Columns

```python
df['total'] = df['price'] * df['quantity']
df['category'] = pd.cut(df['age'], bins=[0, 18, 35, 60, 100],
                        labels=['child', 'young', 'middle', 'senior'])
```

## Aggregation

```python
# Single function
df.groupby('city')['salary'].mean()

# Multiple functions
df.groupby('city')['salary'].agg(['mean', 'median', 'std'])

# Multiple columns
df.groupby(['city', 'dept']).agg({
    'salary': ['mean', 'max'],
    'hire_date': 'min'
}).reset_index()
```

## Pivot Tables

```python
df.pivot_table(
    values='sales',
    index='store',
    columns='quarter',
    aggfunc='sum',
    fill_value=0
)
```

## Counting

```python
df['category'].value_counts()                    # Counts
df['category'].value_counts(normalize=True)      # Proportions
df.drop_duplicates(subset=['name', 'year'])      # Unique combos
```

## Cumulative Statistics

```python
df['running_total'] = df['sales'].cumsum()
df['cumulative_max'] = df['sales'].cummax()
```

## Merging

```python
# Inner join (default)
pd.merge(df1, df2, on='id')

# Left join
pd.merge(df1, df2, on='id', how='left')

# Join on different column names
pd.merge(df1, df2, left_on='user_id', right_on='id')
```

## Key Takeaways

- `info()` and `describe()` are your first steps with any new DataFrame
- Use `isin()` for filtering on multiple categorical values
- `groupby().agg()` lets you compute multiple stats on multiple columns
- `pivot_table` is an alternative to `groupby` for cross-tabulation
- Always use parentheses: `df[(df['a'] > 1) & (df['b'] < 2)]`
