---
created: '2026-07-16'
difficulty: medium
tags:
- python
- visualization
- seaborn
- matplotlib
topic: fullstack
---

# Data Visualization with Seaborn and Matplotlib

Seaborn makes statistical visualization easy by handling complexity behind the scenes. Built on Matplotlib, it works seamlessly with Pandas DataFrames.

## Setup

```python
import seaborn as sns
import matplotlib.pyplot as plt

# Load Seaborn's built-in datasets
tips = sns.load_dataset('tips')
```

## Scatter Plots (Relationships)

```python
# Basic scatter
sns.scatterplot(x='total_bill', y='tip', data=tips)
plt.show()

# With subgroups (hue = color, style = marker)
sns.scatterplot(x='total_bill', y='tip',
                hue='smoker', style='sex',
                size='size', alpha=0.7,
                data=tips)
plt.show()

# Relplot for faceted subplots
sns.relplot(x='total_bill', y='tip',
            col='time', row='sex',
            kind='scatter', data=tips)
plt.show()
```

## Line Plots (Time Series)

```python
# Aggregates multiple observations into mean + confidence interval
sns.relplot(x='timepoint', y='signal',
            kind='line', hue='region',
            style='event', data=df)

# Remove confidence interval
sns.lineplot(x='timepoint', y='signal',
             ci=None, data=df)

# Show standard deviation instead of CI
sns.lineplot(x='timepoint', y='signal',
             ci='sd', data=df)
```

## Categorical Plots

```python
# Bar plot (shows confidence interval)
sns.barplot(x='day', y='total_bill', hue='sex', data=tips)

# Count plot (frequency of categories)
sns.countplot(x='species', data=iris)

# Box plot (distribution + outliers)
sns.boxplot(x='day', y='total_bill', data=tips)

# Violin plot (density distribution)
sns.violinplot(x='day', y='total_bill', data=tips)
```

## Histograms (Distribution)

```python
sns.histplot(data=tips, x='total_bill', bins=20, kde=True)
sns.displot(data=tips, x='total_bill', col='time', row='sex')
```

## Heatmaps (Correlations)

```python
corr = df.corr()
sns.heatmap(corr, annot=True, cmap='coolwarm', center=0)
```

## Pair Plots

```python
# Scatter matrix for all numeric columns
sns.pairplot(iris, hue='species')
```

## Customization

```python
# Figure size
plt.figure(figsize=(10, 6))

# Titles and labels
plt.title('Sales by Region')
plt.xlabel('Region')
plt.ylabel('Revenue ($)')

# Style
sns.set_style('whitegrid')    # darkgrid, whitegrid, dark, white, ticks
sns.set_palette('husl')        # Color palette

# Save
plt.savefig('plot.png', dpi=300, bbox_inches='tight')
```

## Tidy Data Requirement

Seaborn expects tidy data: each row = one observation, each column = one variable.

```python
# Bad: wide format
# city    jan    feb    mar
# NYC     100    120    130

# Good: tidy format
# city    month    temp
# NYC     jan      100
# NYC     feb      120
```

## Key Takeaways

- `scatterplot` for 2 quantitative variables, add `hue`/`style` for subgroups
- `relplot` creates faceted subplots (`col`, `row` parameters)
- `lineplot` for time series; aggregates to mean + CI by default
- `boxplot`/`violinplot` for distribution comparison across categories
- `heatmap` for correlation matrices — always annotate with `annot=True`
- Seaborn requires tidy data format for DataFrame-based plots
