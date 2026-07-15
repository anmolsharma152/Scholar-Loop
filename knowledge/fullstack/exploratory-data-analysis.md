---
created: '2026-07-16'
difficulty: medium
tags:
- python
- eda
- statistics
- pandas
topic: fullstack
---

# Exploratory Data Analysis (EDA)

EDA is the process of understanding your data before modeling. The goal: answer questions, find patterns, and guide decisions using summaries and visualizations.

## The EDA Workflow

1. **Inspect** — shape, dtypes, head, info
2. **Validate** — value_counts, describe, check against codebook
3. **Clean** — missing values, duplicates, wrong types
4. **Filter** — remove outliers, subset to relevant data
5. **Visualize** — distributions, relationships, trends
6. **Summarize** — PMFs, CDFs, correlation matrices

## Inspecting and Validating

```python
df.shape              # (rows, cols)
df.info()             # Column types, non-null counts
df.describe()         # Numeric summary stats
df.head()             # First 5 rows

# Check categorical distributions
df['category'].value_counts()

# Check for outliers
df['age'].describe()
```

## Handling Missing Values

```python
# Identify
df.isna().sum()

# Replace specific codes with NaN
df['weight'] = df['weight'].replace([98, 99], np.nan)

# Drop rows with NaN in specific columns
df = df.dropna(subset=['weight', 'age'])

# Impute with mean/median
df['age'].fillna(df['age'].median(), inplace=True)
```

## Resampling (Correcting for Oversampling)

When data is oversampled (e.g., over-representing minorities), use sampling weights:

```python
# Weighted resampling
weighted_df = df.sample(n=len(df), weights='survey_weight', replace=True)
```

## Distributions

**Histogram** — shows frequency of values in bins:
```python
import matplotlib.pyplot as plt
plt.hist(df['birth_weight'].dropna(), bins=20)
plt.xlabel('Birth Weight (lbs)')
plt.ylabel('Frequency')
plt.show()
```

**PMF (Probability Mass Function)** — unique values and their frequencies:
```python
from empiricaldist import Pmf
pmf = Pmf.from_seq(df['education'], normalize=True)
pmf.bar()
plt.xlabel('Years of Education')
plt.ylabel('Proportion')
plt.show()
```

**CDF (Cumulative Distribution Function)** — fraction of values below x:
```python
from empiricaldist import Cdf
cdf = Cdf.from_seq(df['income'])
cdf.plot()
plt.xlabel('Income')
plt.ylabel('Cumulative Probability')
plt.show()
```

## Comparing Groups

```python
# Boolean filtering
preterm = df[df['gestation'] < 37]
full_term = df[df['gestation'] >= 37]

# Compare means
preterm['weight'].mean(), full_term['weight'].mean()

# Logical operators for complex filters
df[(df['age'] > 20) & (df['age'] < 35) & (df['income'] > 50000)]
```

## Probability and Statistics

```python
# Boolean Series as 0/1
(df['premature'] == True).mean()    # Fraction of preterm births

# Conditional probability
df[df['smoker'] == 'yes']['birth_weight'].mean()

# Correlation
df[['age', 'income', 'education']].corr()
```

## Key Takeaways

- Always validate data against a codebook before analysis
- Replace sentinel values (98, 99) with NaN — they skew statistics
- Histograms show bins; PMFs show exact values — use PMF for small datasets
- CDFs are better than histograms for comparing distributions
- Use sampling weights when data is oversampled
- `mean()` of a Boolean Series gives the fraction of True values
