from __future__ import annotations

import shlex
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
ROOT_DIR = PROJECT_DIR.parents[0]
sys.path.insert(0, str(ROOT_DIR / "common"))

from stats_toolkit import (  # noqa: E402
    bootstrap_ci,
    download_zip,
    ensure_dir,
    fmt,
    markdown_table,
    mean,
    multiple_linear_regression,
    permutation_mean_difference,
    proportion,
    simple_linear_regression,
    summary_rows,
    write_bar_svg,
    write_histogram_svg,
    write_scatter_svg,
)


SOURCE_URL = "https://archive.ics.uci.edu/static/public/9/auto+mpg.zip"
SOURCE_PAGE = "https://archive.ics.uci.edu/dataset/9/auto+mpg"


def prepare_data() -> list[dict[str, object]]:
    data_dir = PROJECT_DIR / "data"
    raw_dir = data_dir / "raw"
    ensure_dir(raw_dir)
    archive = download_zip(SOURCE_URL, raw_dir / "auto_mpg.zip")
    for name in ["auto-mpg.data", "auto-mpg.names"]:
        target = raw_dir / name
        if not target.exists():
            target.write_bytes(archive.read(name))

    rows: list[dict[str, object]] = []
    for line in (raw_dir / "auto-mpg.data").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        parts = shlex.split(line)
        horsepower = None if parts[3] == "?" else float(parts[3])
        rows.append({
            "mpg": float(parts[0]),
            "cylinders": float(parts[1]),
            "displacement": float(parts[2]),
            "horsepower": horsepower,
            "weight": float(parts[4]),
            "acceleration": float(parts[5]),
            "model_year": float(parts[6]),
            "origin": int(float(parts[7])),
            "car_name": parts[8],
        })
    return rows


def main() -> None:
    rows = prepare_data()
    model_rows = [row for row in rows if row["horsepower"] is not None]
    output_dir = PROJECT_DIR / "output"
    chart_dir = output_dir / "charts"
    ensure_dir(chart_dir)

    mpg = [float(row["mpg"]) for row in rows]
    horsepower = [float(row["horsepower"]) for row in model_rows]
    weight = [float(row["weight"]) for row in model_rows]
    cylinders = [float(row["cylinders"]) for row in model_rows]
    model_year = [float(row["model_year"]) for row in model_rows]

    mean_ci = bootstrap_ci(mpg, mean, iterations=5000, seed=310)
    us_mpg = [float(row["mpg"]) for row in rows if int(row["origin"]) == 1]
    imported_mpg = [float(row["mpg"]) for row in rows if int(row["origin"]) != 1]
    origin_test = permutation_mean_difference(imported_mpg, us_mpg, iterations=8000, seed=311)

    features = [
        [
            float(row["weight"]) / 1000,
            float(row["horsepower"]) / 10,
            float(row["cylinders"]),
            float(row["model_year"]) - 70,
            1.0 if int(row["origin"]) == 2 else 0.0,
            1.0 if int(row["origin"]) == 3 else 0.0,
        ]
        for row in model_rows
    ]
    target = [float(row["mpg"]) for row in model_rows]
    model = multiple_linear_regression(
        features,
        target,
        ["weight_1000_lb", "horsepower_10", "cylinders", "model_year_since_1970", "europe_origin", "japan_origin"],
    )

    weight_regression = simple_linear_regression([value / 1000 for value in weight], target)
    write_scatter_svg(chart_dir / "weight_vs_mpg.svg", [value / 1000 for value in weight], target, "Vehicle Weight and Fuel Economy", "Weight (1000 lb)", "MPG", weight_regression)
    write_histogram_svg(chart_dir / "mpg_distribution.svg", mpg, "MPG Distribution", "Miles per gallon", bins=12)

    year_labels = [str(year) for year in range(70, 83)]
    year_means = [
        mean([float(row["mpg"]) for row in rows if int(float(row["model_year"])) == year])
        for year in range(70, 83)
    ]
    write_bar_svg(chart_dir / "mean_mpg_by_year.svg", year_labels, year_means, "Mean MPG by Model Year", "Mean MPG")

    probabilities = {
        "P(MPG >= 30)": proportion(rows, lambda row: float(row["mpg"]) >= 30),
        "P(MPG >= 30 | model year >= 1980)": proportion(
            [row for row in rows if float(row["model_year"]) >= 80],
            lambda row: float(row["mpg"]) >= 30,
        ),
        "P(US origin | MPG < 20)": proportion(
            [row for row in rows if float(row["mpg"]) < 20],
            lambda row: int(row["origin"]) == 1,
        ),
    }

    coefficients = model["coefficients"]
    report = f"""# Auto MPG Regression Analysis

## Research Question

How much do vehicle weight, horsepower, cylinders, model year, and origin explain city-cycle fuel efficiency?

## Dataset

Source: [UCI Auto MPG]({SOURCE_PAGE}). The dataset contains {len(rows)} vehicles from the 1970-1982 model years. Regression uses {len(model_rows)} records after excluding rows with missing horsepower.

## Methods Used

- Descriptive statistics for MPG and vehicle specifications.
- Inferential statistics through a bootstrap confidence interval for mean MPG.
- Hypothesis testing through a permutation test comparing imported and US-origin vehicles.
- Regression analysis using ordinary least squares.
- Probability through empirical and conditional probability statements.
- Research methods through a defined modeling question, variable choices, missing-data rule, and non-causal interpretation.

## Descriptive Statistics

{markdown_table(["Variable", "n", "Mean", "Median", "SD", "Min", "Q1", "Q3", "Max"], summary_rows({
    "MPG": mpg,
    "Horsepower": horsepower,
    "Weight": weight,
    "Cylinders": cylinders,
    "Model year": model_year,
}))}

## Inferential Statistics

The bootstrap 95% confidence interval for mean MPG is **{fmt(mean_ci[0])} to {fmt(mean_ci[1])}**.

## Hypothesis Test

Null hypothesis: imported and US-origin vehicles have the same mean MPG.

Observed difference, imported minus US-origin: **{fmt(origin_test["difference"])} MPG**.

Permutation p-value: **{fmt(origin_test["p_value"], 4)}**.

## Regression Analysis

Model: `mpg ~ weight_1000_lb + horsepower_10 + cylinders + model_year_since_1970 + europe_origin + japan_origin`

{markdown_table(["Term", "Coefficient"], [[term, fmt(value)] for term, value in coefficients.items()])}

Model R-squared: **{fmt(float(model["r2"]))}**. RMSE: **{fmt(float(model["rmse"]))} MPG**.

## Probability Findings

{markdown_table(["Probability statement", "Estimate"], [[label, fmt(value)] for label, value in probabilities.items()])}

## Portfolio Interpretation

Weight and model year are practical fuel-economy signals: heavier vehicles tend to have lower MPG, while newer model years show improved efficiency. Origin differences are statistically visible in the dataset, but the model treats them as associations in historical vehicle data rather than causal effects.

## Reproducibility

Run:

```bash
python statistics_projects/auto_mpg_regression/analyze.py
```

Generated charts are saved in `output/charts/`.
"""
    (output_dir / "report.md").write_text(report, encoding="utf-8")

    print("Auto MPG regression study complete")
    print(f"Report: {output_dir / 'report.md'}")


if __name__ == "__main__":
    main()
