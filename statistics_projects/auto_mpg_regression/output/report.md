# Auto MPG Regression Analysis

## Research Question

How much do vehicle weight, horsepower, cylinders, model year, and origin explain city-cycle fuel efficiency?

## Dataset

Source: [UCI Auto MPG](https://archive.ics.uci.edu/dataset/9/auto+mpg). The dataset contains 398 vehicles from the 1970-1982 model years. Regression uses 392 records after excluding rows with missing horsepower.

## Methods Used

- Descriptive statistics for MPG and vehicle specifications.
- Inferential statistics through a bootstrap confidence interval for mean MPG.
- Hypothesis testing through a permutation test comparing imported and US-origin vehicles.
- Regression analysis using ordinary least squares.
- Probability through empirical and conditional probability statements.
- Research methods through a defined modeling question, variable choices, missing-data rule, and non-causal interpretation.

## Descriptive Statistics

| Variable | n | Mean | Median | SD | Min | Q1 | Q3 | Max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MPG | 398 | 23.51 | 23.00 | 7.816 | 9.000 | 17.50 | 29.00 | 46.60 |
| Horsepower | 392 | 104.5 | 93.50 | 38.49 | 46.00 | 75.00 | 126.0 | 230.0 |
| Weight | 392 | 2977.6 | 2803.5 | 849.4 | 1613.0 | 2225.2 | 3614.8 | 5140.0 |
| Cylinders | 392 | 5.472 | 4.000 | 1.706 | 3.000 | 4.000 | 8.000 | 8.000 |
| Model year | 392 | 75.98 | 76.00 | 3.684 | 70.00 | 73.00 | 79.00 | 82.00 |

## Inferential Statistics

The bootstrap 95% confidence interval for mean MPG is **22.76 to 24.31**.

## Hypothesis Test

Null hypothesis: imported and US-origin vehicles have the same mean MPG.

Observed difference, imported minus US-origin: **9.165 MPG**.

Permutation p-value: **0.0001**.

## Regression Analysis

Model: `mpg ~ weight_1000_lb + horsepower_10 + cylinders + model_year_since_1970 + europe_origin + japan_origin`

| Term | Coefficient |
| --- | --- |
| intercept | 35.44 |
| weight_1000_lb | -5.737 |
| horsepower_10 | -0.100 |
| cylinders | 0.143 |
| model_year_since_1970 | 0.758 |
| europe_origin | 2.035 |
| japan_origin | 2.328 |

Model R-squared: **0.820**. RMSE: **3.311 MPG**.

## Probability Findings

| Probability statement | Estimate |
| --- | --- |
| P(MPG >= 30) | 0.231 |
| P(MPG >= 30 | model year >= 1980) | 0.629 |
| P(US origin | MPG < 20) | 0.940 |

## Portfolio Interpretation

Weight and model year are practical fuel-economy signals: heavier vehicles tend to have lower MPG, while newer model years show improved efficiency. Origin differences are statistically visible in the dataset, but the model treats them as associations in historical vehicle data rather than causal effects.

## Reproducibility

Run:

```bash
python statistics_projects/auto_mpg_regression/analyze.py
```

Generated charts are saved in `output/charts/`.
