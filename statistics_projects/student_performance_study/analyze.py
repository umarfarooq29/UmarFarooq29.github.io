from __future__ import annotations

import sys
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile


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
    read_csv,
    simple_linear_regression,
    summary_rows,
    write_bar_svg,
    write_histogram_svg,
    write_scatter_svg,
)


SOURCE_URL = "https://archive.ics.uci.edu/static/public/320/student+performance.zip"
SOURCE_PAGE = "https://archive.ics.uci.edu/dataset/320/student+performance"


def prepare_data() -> list[dict[str, object]]:
    data_dir = PROJECT_DIR / "data"
    raw_dir = data_dir / "raw"
    ensure_dir(raw_dir)

    outer_zip = download_zip(SOURCE_URL, raw_dir / "student_performance.zip")
    nested_bytes = outer_zip.read("student.zip")
    with ZipFile(BytesIO(nested_bytes)) as nested:
        for name in ["student-por.csv", "student-mat.csv", "student.txt"]:
            target = raw_dir / name
            if not target.exists():
                target.write_bytes(nested.read(name))

    rows = read_csv(raw_dir / "student-por.csv", delimiter=";")
    numeric_fields = [
        "age",
        "Medu",
        "Fedu",
        "traveltime",
        "studytime",
        "failures",
        "famrel",
        "freetime",
        "goout",
        "Dalc",
        "Walc",
        "health",
        "absences",
        "G1",
        "G2",
        "G3",
    ]
    cleaned: list[dict[str, object]] = []
    for row in rows:
        item: dict[str, object] = dict(row)
        for field in numeric_fields:
            item[field] = float(row[field])
        item["internet_yes"] = 1.0 if row["internet"] == "yes" else 0.0
        item["passed"] = 1.0 if item["G3"] >= 10 else 0.0
        cleaned.append(item)
    return cleaned


def main() -> None:
    rows = prepare_data()
    output_dir = PROJECT_DIR / "output"
    chart_dir = output_dir / "charts"
    ensure_dir(chart_dir)

    grades = [float(row["G3"]) for row in rows]
    studytime = [float(row["studytime"]) for row in rows]
    absences = [float(row["absences"]) for row in rows]
    failures = [float(row["failures"]) for row in rows]
    g1 = [float(row["G1"]) for row in rows]
    g2 = [float(row["G2"]) for row in rows]
    internet_yes = [row for row in rows if row["internet"] == "yes"]
    internet_no = [row for row in rows if row["internet"] == "no"]

    mean_ci = bootstrap_ci(grades, mean, iterations=5000, seed=210)
    internet_test = permutation_mean_difference(
        [float(row["G3"]) for row in internet_yes],
        [float(row["G3"]) for row in internet_no],
        iterations=8000,
        seed=211,
    )

    features = [
        [
            float(row["G1"]),
            float(row["G2"]),
            float(row["studytime"]),
            float(row["failures"]),
            float(row["absences"]) / 10,
            float(row["internet_yes"]),
        ]
        for row in rows
    ]
    model = multiple_linear_regression(
        features,
        grades,
        ["G1", "G2", "studytime", "failures", "absences_per_10", "internet_yes"],
    )

    predicted = [float(value) for value in model["predictions"]]
    prediction_line = simple_linear_regression(predicted, grades)

    study_labels = ["<2h", "2-5h", "5-10h", ">10h"]
    study_means = [
        mean([float(row["G3"]) for row in rows if int(float(row["studytime"])) == level])
        for level in range(1, 5)
    ]

    write_histogram_svg(chart_dir / "final_grade_distribution.svg", grades, "Final Grade Distribution", "Final grade (0-20)", bins=11)
    write_bar_svg(chart_dir / "mean_grade_by_study_time.svg", study_labels, study_means, "Mean Grade by Study Time", "Mean final grade")
    write_scatter_svg(chart_dir / "actual_vs_predicted.svg", predicted, grades, "Actual vs Predicted Grades", "Predicted grade", "Actual grade", prediction_line)

    probabilities = {
        "P(pass)": proportion(rows, lambda row: float(row["G3"]) >= 10),
        "P(pass | studytime >= 5h)": proportion(
            [row for row in rows if float(row["studytime"]) >= 3],
            lambda row: float(row["G3"]) >= 10,
        ),
        "P(high grade >= 15 | no failures)": proportion(
            [row for row in rows if float(row["failures"]) == 0],
            lambda row: float(row["G3"]) >= 15,
        ),
    }

    coefficients = model["coefficients"]
    report = f"""# Student Performance Research Study

## Research Question

Which academic and background factors are associated with final Portuguese course grades, and is there evidence that students with internet access have different average final grades?

## Dataset

Source: [UCI Student Performance]({SOURCE_PAGE}). The analysis uses `student-por.csv`, which contains {len(rows)} student records collected from two Portuguese secondary schools through school reports and questionnaires.

## Methods Used

- Descriptive statistics for final grade, study time, absences, previous grades, and failures.
- Inferential statistics through a bootstrap confidence interval for mean final grade.
- Hypothesis testing through a permutation test comparing students with and without internet access.
- Regression analysis using an ordinary least squares model for final grade.
- Probability through empirical pass and high-grade conditional probabilities.
- Research methods through a clearly defined question, variables, assumptions, and interpretation limits.

## Descriptive Statistics

{markdown_table(["Variable", "n", "Mean", "Median", "SD", "Min", "Q1", "Q3", "Max"], summary_rows({
    "Final grade G3": grades,
    "First period grade G1": g1,
    "Second period grade G2": g2,
    "Study time level": studytime,
    "Absences": absences,
    "Past failures": failures,
}))}

## Inferential Statistics

The bootstrap 95% confidence interval for the mean final grade is **{fmt(mean_ci[0])} to {fmt(mean_ci[1])}**.

## Hypothesis Test

Null hypothesis: mean final grade is the same for students with and without internet access.

Observed difference, internet yes minus no: **{fmt(internet_test["difference"])} grade points**.

Permutation p-value: **{fmt(internet_test["p_value"], 4)}**.

## Regression Analysis

Model: `G3 ~ G1 + G2 + studytime + failures + absences_per_10 + internet_yes`

{markdown_table(["Term", "Coefficient"], [[term, fmt(value)] for term, value in coefficients.items()])}

Model R-squared: **{fmt(float(model["r2"]))}**. RMSE: **{fmt(float(model["rmse"]))} grade points**.

## Probability Findings

{markdown_table(["Probability statement", "Estimate"], [[label, fmt(value)] for label, value in probabilities.items()])}

## Portfolio Interpretation

Previous grades are the strongest predictors of final performance, while failures and absences add useful warning signals. The internet-access comparison is framed carefully as association, not causation, because this is observational school data.

## Reproducibility

Run:

```bash
python statistics_projects/student_performance_study/analyze.py
```

Generated charts are saved in `output/charts/`.
"""
    (output_dir / "report.md").write_text(report, encoding="utf-8")

    print("Student performance study complete")
    print(f"Report: {output_dir / 'report.md'}")


if __name__ == "__main__":
    main()
