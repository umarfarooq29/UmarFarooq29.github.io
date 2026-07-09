from __future__ import annotations

import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
ROOT_DIR = PROJECT_DIR.parents[0]
sys.path.insert(0, str(ROOT_DIR / "common"))

from stats_toolkit import (  # noqa: E402
    bootstrap_ci,
    bootstrap_pair_ci,
    ensure_dir,
    fmt,
    markdown_table,
    mean,
    permutation_regression_slope,
    proportion,
    simple_linear_regression,
    summary_rows,
    write_csv,
    write_histogram_svg,
    write_scatter_svg,
)


SOURCE_PAGE = "https://www.openintro.org/data/index.php?data=bac"


BAC_ROWS = [
    {"student": 1, "beers": 5, "bac": 0.10},
    {"student": 2, "beers": 2, "bac": 0.03},
    {"student": 3, "beers": 9, "bac": 0.19},
    {"student": 4, "beers": 8, "bac": 0.12},
    {"student": 5, "beers": 3, "bac": 0.04},
    {"student": 6, "beers": 7, "bac": 0.095},
    {"student": 7, "beers": 3, "bac": 0.07},
    {"student": 8, "beers": 5, "bac": 0.06},
    {"student": 9, "beers": 3, "bac": 0.02},
    {"student": 10, "beers": 5, "bac": 0.05},
    {"student": 11, "beers": 4, "bac": 0.07},
    {"student": 12, "beers": 6, "bac": 0.10},
    {"student": 13, "beers": 5, "bac": 0.085},
    {"student": 14, "beers": 7, "bac": 0.09},
    {"student": 15, "beers": 1, "bac": 0.01},
    {"student": 16, "beers": 4, "bac": 0.05},
]


def prepare_data() -> list[dict[str, object]]:
    data_dir = PROJECT_DIR / "data"
    write_csv(data_dir / "bac.csv", BAC_ROWS, ["student", "beers", "bac"])
    return [dict(row) for row in BAC_ROWS]


def main() -> None:
    rows = prepare_data()
    output_dir = PROJECT_DIR / "output"
    chart_dir = output_dir / "charts"
    ensure_dir(chart_dir)

    beers = [float(row["beers"]) for row in rows]
    bac = [float(row["bac"]) for row in rows]

    model = simple_linear_regression(beers, bac)
    slope_ci = bootstrap_pair_ci(
        beers,
        bac,
        lambda x_values, y_values: simple_linear_regression(x_values, y_values)["slope"],
        iterations=5000,
        seed=410,
    )
    mean_ci = bootstrap_ci(bac, mean, iterations=5000, seed=411)
    slope_test = permutation_regression_slope(beers, bac, iterations=10000, seed=412, alternative="greater")

    write_scatter_svg(chart_dir / "beers_vs_bac.svg", beers, bac, "Beers Consumed and BAC", "Number of beers", "Blood alcohol content", model)
    write_histogram_svg(chart_dir / "bac_distribution.svg", bac, "BAC Distribution", "Blood alcohol content", bins=8)

    probabilities = {
        "P(BAC >= 0.08)": proportion(rows, lambda row: float(row["bac"]) >= 0.08),
        "P(BAC >= 0.08 | beers >= 5)": proportion(
            [row for row in rows if float(row["beers"]) >= 5],
            lambda row: float(row["bac"]) >= 0.08,
        ),
        "P(BAC < 0.05 | beers <= 3)": proportion(
            [row for row in rows if float(row["beers"]) <= 3],
            lambda row: float(row["bac"]) < 0.05,
        ),
    }

    report = f"""# BAC Probability and Hypothesis Testing Experiment

## Research Question

In a small controlled student-volunteer experiment, how strongly does the number of beers consumed predict blood alcohol content?

## Dataset

Source: [OpenIntro Beer and Blood Alcohol Content]({SOURCE_PAGE}). The dataset contains {len(rows)} Ohio State student volunteers who were randomly assigned a number of beers and then measured for BAC.

## Methods Used

- Descriptive statistics for beers consumed and BAC.
- Inferential statistics through bootstrap confidence intervals for mean BAC and the regression slope.
- Hypothesis testing through a permutation test for a positive beer-to-BAC relationship.
- Regression analysis using simple ordinary least squares.
- Probability through empirical conditional probabilities.
- Research methods through an experimental setup, random assignment context, and small-sample limitations.

## Descriptive Statistics

{markdown_table(["Variable", "n", "Mean", "Median", "SD", "Min", "Q1", "Q3", "Max"], summary_rows({
    "Beers": beers,
    "BAC": bac,
}))}

## Inferential Statistics

The bootstrap 95% confidence interval for mean BAC is **{fmt(mean_ci[0], 4)} to {fmt(mean_ci[1], 4)}**.

The bootstrap 95% confidence interval for the regression slope is **{fmt(slope_ci[0], 4)} to {fmt(slope_ci[1], 4)} BAC units per beer**.

## Hypothesis Test

Null hypothesis: there is no positive relationship between beers consumed and BAC.

Observed slope: **{fmt(slope_test["slope"], 4)} BAC units per beer**.

One-sided permutation p-value: **{fmt(slope_test["p_value"], 4)}**.

## Regression Analysis

Model: `BAC = {fmt(model["intercept"], 4)} + {fmt(model["slope"], 4)} * beers`

Correlation: **{fmt(model["r"])}**. R-squared: **{fmt(model["r2"])}**. RMSE: **{fmt(model["rmse"], 4)} BAC units**.

## Probability Findings

{markdown_table(["Probability statement", "Estimate"], [[label, fmt(value)] for label, value in probabilities.items()])}

## Portfolio Interpretation

The experiment shows a clear positive relationship: each additional beer is associated with an estimated increase of about {fmt(model["slope"], 4)} BAC units. Because the sample is only 16 students, the report emphasizes confidence intervals and exact resampling logic instead of overclaiming.

## Reproducibility

Run:

```bash
python statistics_projects/bac_probability_experiment/analyze.py
```

Generated charts are saved in `output/charts/`.
"""
    (output_dir / "report.md").write_text(report, encoding="utf-8")

    print("BAC probability experiment complete")
    print(f"Report: {output_dir / 'report.md'}")


if __name__ == "__main__":
    main()
