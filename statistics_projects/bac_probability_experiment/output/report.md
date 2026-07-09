# BAC Probability and Hypothesis Testing Experiment

## Research Question

In a small controlled student-volunteer experiment, how strongly does the number of beers consumed predict blood alcohol content?

## Dataset

Source: [OpenIntro Beer and Blood Alcohol Content](https://www.openintro.org/data/index.php?data=bac). The dataset contains 16 Ohio State student volunteers who were randomly assigned a number of beers and then measured for BAC.

## Methods Used

- Descriptive statistics for beers consumed and BAC.
- Inferential statistics through bootstrap confidence intervals for mean BAC and the regression slope.
- Hypothesis testing through a permutation test for a positive beer-to-BAC relationship.
- Regression analysis using simple ordinary least squares.
- Probability through empirical conditional probabilities.
- Research methods through an experimental setup, random assignment context, and small-sample limitations.

## Descriptive Statistics

| Variable | n | Mean | Median | SD | Min | Q1 | Q3 | Max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Beers | 16 | 4.812 | 5.000 | 2.198 | 1.000 | 3.000 | 6.250 | 9.000 |
| BAC | 16 | 0.074 | 0.070 | 0.044 | 0.010 | 0.048 | 0.096 | 0.190 |

## Inferential Statistics

The bootstrap 95% confidence interval for mean BAC is **0.0541 to 0.0956**.

The bootstrap 95% confidence interval for the regression slope is **0.0122 to 0.0231 BAC units per beer**.

## Hypothesis Test

Null hypothesis: there is no positive relationship between beers consumed and BAC.

Observed slope: **0.0180 BAC units per beer**.

One-sided permutation p-value: **0.0001**.

## Regression Analysis

Model: `BAC = -0.0127 + 0.0180 * beers`

Correlation: **0.894**. R-squared: **0.800**. RMSE: **0.0191 BAC units**.

## Probability Findings

| Probability statement | Estimate |
| --- | --- |
| P(BAC >= 0.08) | 0.438 |
| P(BAC >= 0.08 | beers >= 5) | 0.778 |
| P(BAC < 0.05 | beers <= 3) | 0.800 |

## Portfolio Interpretation

The experiment shows a clear positive relationship: each additional beer is associated with an estimated increase of about 0.0180 BAC units. Because the sample is only 16 students, the report emphasizes confidence intervals and exact resampling logic instead of overclaiming.

## Reproducibility

Run:

```bash
python statistics_projects/bac_probability_experiment/analyze.py
```

Generated charts are saved in `output/charts/`.
