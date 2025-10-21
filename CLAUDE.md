# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Data Science course repository for 2025 2학기 데이터과학기초(ITEC0419) 002분반. It contains Jupyter notebooks covering statistical inference topics including sampling, hypothesis testing, A/B testing, causality, bootstrapping, and confidence intervals.

## Environment Setup

The notebooks are designed to run in Google Colab and use the `datascience` library (UC Berkeley's Data 8 library):

```python
!pip install datascience
from datascience import *
import numpy as np
import matplotlib.pyplot as plots
plots.style.use('fivethirtyeight')
%matplotlib inline
```

**Google Drive Integration:** Most notebooks mount Google Drive to access data files:
```python
from google.colab import drive
drive.mount('/content/gdrive')
path_data = '/content/gdrive/MyDrive/DataScience/data/'
```

## Notebook Organization

Notebooks are organized by chapter in the `notebooks/` directory:

- **Chapter 10**: Sampling and Empirical Distributions
  - `10.0`: Introduction to sampling and empirical distributions
  - `10.1`: Empirical distributions
  - `10.2`: Sampling from a population
  - `10.3`: Empirical distribution of a statistic
  - `10.4`: Random sampling in Python

- **Chapter 11**: Testing Hypotheses
  - `11.1`: Assessing a model
  - `11.2`: Multiple categories
  - `11.3`: Decisions and uncertainty
  - `11.4`: Error probabilities

- **Chapter 12**: Comparison and Causality
  - `12.1`: A/B testing
  - `12.2`: Causality
  - `12.3`: Deflategate case study

- **Chapter 13**: Estimation
  - `13.1`: Percentiles
  - `13.2`: Bootstrap (largest notebook with extensive bootstrap methodology)
  - `13.3`: Confidence intervals
  - `13.4`: Using confidence intervals

## Key Library: datascience

The `datascience` library provides a `Table` class with methods:

- **Reading data**: `Table.read_table(path)`
- **Sampling**: `table.sample(n, with_replacement=True/False)`
- **Filtering**: `table.where(column, predicate)`
- **Sorting**: `table.sort(column, descending=False)`
- **Selection**: `table.select(columns)`, `table.take(indices)`
- **Visualization**: `table.hist(bins=...)`, etc.
- **Statistics**: Use `percentile(p, array)` for percentiles

## Common Patterns

**Bootstrap resampling pattern:**
```python
def bootstrap_statistic(original_sample, num_repetitions):
    statistics = make_array()
    for i in np.arange(num_repetitions):
        resample = original_sample.sample()  # with replacement by default
        stat = compute_statistic(resample)
        statistics = np.append(statistics, stat)
    return statistics
```

**Confidence interval calculation:**
```python
left_end = percentile(2.5, bootstrap_statistics)
right_end = percentile(97.5, bootstrap_statistics)
```

## Working with Notebooks

- Notebooks assume Google Colab environment with drive mounted
- Data paths use `/content/gdrive/MyDrive/DataScience/data/`
- Some notebooks have cell execution errors (e.g., `NameError: name 'make_array' is not defined`) when cells are run out of order
- Always run import cells first before running analysis cells
- Large simulations (e.g., bootstrap with 5000+ iterations) can take several minutes
