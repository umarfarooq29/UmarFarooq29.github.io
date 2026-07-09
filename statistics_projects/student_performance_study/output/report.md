# Student Performance Research Study

## Research Question

Which academic and background factors are associated with final Portuguese course grades, and is there evidence that students with internet access have different average final grades?

## Dataset

Source: [UCI Student Performance](https://archive.ics.uci.edu/dataset/320/student+performance). The analysis uses `student-por.csv`, which contains 649 student records collected from two Portuguese secondary schools through school reports and questionnaires.

## Methods Used

- Descriptive statistics for final grade, study time, absences, previous grades, and failures.
- Inferential statistics through a bootstrap confidence interval for mean final grade.
- Hypothesis testing through a permutation test comparing students with and without internet access.
- Regression analysis using an ordinary least squares model for final grade.
- Probability through empirical pass and high-grade conditional probabilities.
- Research methods through a clearly defined question, variables, assumptions, and interpretation limits.

## Descriptive Statistics

| Variable | n | Mean | Median | SD | Min | Q1 | Q3 | Max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Final grade G3 | 649 | 11.91 | 12.00 | 3.231 | 0.000 | 10.00 | 14.00 | 19.00 |
| First period grade G1 | 649 | 11.40 | 11.00 | 2.745 | 0.000 | 10.00 | 13.00 | 19.00 |
| Second period grade G2 | 649 | 11.57 | 11.00 | 2.914 | 0.000 | 10.00 | 13.00 | 19.00 |
| Study time level | 649 | 1.931 | 2.000 | 0.830 | 1.000 | 1.000 | 2.000 | 4.000 |
| Absences | 649 | 3.659 | 2.000 | 4.641 | 0.000 | 0.000 | 6.000 | 32.00 |
| Past failures | 649 | 0.222 | 0.000 | 0.593 | 0.000 | 0.000 | 0.000 | 3.000 |

## Inferential Statistics

The bootstrap 95% confidence interval for the mean final grade is **11.65 to 12.16**.

## Hypothesis Test

Null hypothesis: mean final grade is the same for students with and without internet access.

Observed difference, internet yes minus no: **1.146 grade points**.

Permutation p-value: **0.0002**.

## Regression Analysis

Model: `G3 ~ G1 + G2 + studytime + failures + absences_per_10 + internet_yes`

| Term | Coefficient |
| --- | --- |
| intercept | -0.187 |
| G1 | 0.139 |
| G2 | 0.885 |
| studytime | 0.097 |
| failures | -0.216 |
| absences_per_10 | 0.228 |
| internet_yes | 0.065 |

Model R-squared: **0.851**. RMSE: **1.248 grade points**.

## Probability Findings

| Probability statement | Estimate |
| --- | --- |
| P(pass) | 0.846 |
| P(pass | studytime >= 5h) | 0.932 |
| P(high grade >= 15 | no failures) | 0.235 |

## Portfolio Interpretation

Previous grades are the strongest predictors of final performance, while failures and absences add useful warning signals. The internet-access comparison is framed carefully as association, not causation, because this is observational school data.

## Reproducibility

Run:

```bash
python statistics_projects/student_performance_study/analyze.py
```

Generated charts are saved in `output/charts/`.
