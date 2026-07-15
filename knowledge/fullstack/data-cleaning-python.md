---
created: '2026-07-16'
difficulty: medium
tags:
- python
- pandas
- data-cleaning
topic: fullstack
---

# Data Cleaning in Python

Dirty data — duplicates, wrong types, missing values, outliers — silently corrupts every analysis downstream. Cleaning is the most time-consuming step in data science, and the most important.

## Data Type Constraints

Check types first with `.dtypes` or `.info()`. Common issues:

**Strings stored as numbers:**
```python
df['revenue'] = df['revenue'].str.strip('$').str.replace(',', '').astype(int)
```

**Numbers stored as strings:**
```python
df['ride_duration'] = df['ride_duration'].str.strip(' minutes').astype(int)
```

**Categorical coded as numeric:**
```python
df['user_type'] = df['user_type'].astype('category')
```

Always validate with `assert` after conversion:
```python
assert df['revenue'].dtype == 'int64'
```

## Data Range Constraints

Out-of-range values break analysis. Handle them based on context:

**Drop (only if small proportion):**
```python
too_large = df[df['tire_size'] > 100]
df = df.drop(too_large.index)
```

**Cap at boundary:**
```python
df.loc[df['tire_size'] > 100, 'tire_size'] = 100
```

**Treat as missing, then impute:**
```python
import numpy as np
df.loc[df['tire_size'] > 100, 'tire_size'] = np.nan
```

**Date constraints:**
```python
df['ride_date'] = pd.to_datetime(df['ride_date'])
today = pd.to_datetime('today').date()
df.loc[df['ride_date'].dt.date > today, 'ride_date'] = pd.Timestamp(today)
```

## Uniqueness Constraints

**Find duplicates:**
```python
# Complete duplicates (all columns match)
df.duplicated().sum()

# Subset duplicates (specific columns match)
df.duplicated(subset=['first_name', 'last_name']).sum()
```

**Remove complete duplicates:**
```python
df = df.drop_duplicates()
```

**Merge incomplete duplicates (average numeric, keep first string):**
```python
df = df.groupby(['first_name', 'last_name', 'address']).agg({
    'height': 'mean',
    'weight': 'mean',
    'birth_year': 'min'
}).reset_index()
```

## Membership Constraints

Categorical columns must contain only valid categories:

```python
# Find invalid categories
valid_cats = ['free_rider', 'pay_per_ride', 'monthly_subscriber']
invalid = df[~df['user_type'].isin(valid_cats)]

# Replace invalid with NaN
df.loc[~df['user_type'].isin(valid_cats), 'user_type'] = np.nan
```

## Key Takeaways

- Always inspect `.dtypes` and `.info()` before analysis
- Use `assert` to verify cleaning steps worked
- Drop data only as a last resort — cap, impute, or flag first
- Duplicate detection needs `subset=` for partial matches
- Categorical data must be validated against a known set of categories
