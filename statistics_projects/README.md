# Statistics Portfolio Projects

This folder contains three reproducible statistics projects designed for a portfolio. Each project includes a research question, public dataset source, analysis script, generated charts, and a Markdown report.

## Projects

| Project | Dataset | Main Methods |
| --- | --- | --- |
| Student Performance Research Study | UCI Student Performance | Descriptive statistics, bootstrap inference, hypothesis testing, multiple regression, empirical probability, research methods |
| Auto MPG Regression Analysis | UCI Auto MPG | Descriptive statistics, bootstrap inference, permutation test, multiple regression, conditional probability, modeling assumptions |
| BAC Probability and Hypothesis Testing Experiment | OpenIntro BAC | Descriptive statistics, experimental research methods, regression, permutation testing, bootstrap confidence intervals, probability |

## Run All Analyses

From the portfolio root:

```bash
python statistics_projects/student_performance_study/analyze.py
python statistics_projects/auto_mpg_regression/analyze.py
python statistics_projects/bac_probability_experiment/analyze.py
```

The scripts use only the Python standard library. UCI datasets are downloaded automatically into each project's `data/raw/` folder. The OpenIntro BAC dataset is small and included directly in the script with source attribution.

## Method Coverage

| Method | Where It Appears |
| --- | --- |
| Descriptive Statistics | All three reports summarize central tendency, spread, quartiles, and ranges. |
| Inferential Statistics | Bootstrap confidence intervals for means and model slopes. |
| Hypothesis Testing | Permutation tests for group differences and positive regression slope. |
| Regression Analysis | Multiple regression for grades and MPG; simple regression for BAC. |
| Probability | Empirical and conditional probability statements in every report. |
| Research Methods | Each report states the research question, dataset design, assumptions, and interpretation limits. |

## Portfolio Use

Use these as GitHub case studies or add screenshots of the generated SVG charts to the portfolio. The website project cards already point to the generated reports.
