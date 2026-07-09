from __future__ import annotations

import csv
import math
import random
from pathlib import Path


try:
    import numpy as np  # type: ignore
    import pandas as pd  # type: ignore
except ImportError:  # The script below remains runnable without optional packages.
    np = None
    pd = None


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"
ASSET_DIR = ROOT / "assets"


def sigmoid(value: float) -> float:
    if value < -35:
        return 0.0
    if value > 35:
        return 1.0
    return 1 / (1 + math.exp(-value))


def generate_dataset(path: Path, size: int = 900) -> None:
    if path.exists():
        return
    rng = random.Random(906)
    fields = [
        "customer_id",
        "tenure_months",
        "monthly_charges",
        "support_tickets",
        "late_payments",
        "usage_gb",
        "contract_type",
        "churn",
    ]
    rows = []
    for index in range(1, size + 1):
        tenure = rng.randrange(1, 73)
        contract = rng.choices(["Month-to-month", "One year", "Two year"], weights=[55, 28, 17], k=1)[0]
        monthly = rng.uniform(22, 118)
        tickets = min(8, int(rng.expovariate(0.8)))
        late = rng.choices([0, 1, 2, 3], weights=[72, 18, 7, 3], k=1)[0]
        usage = max(5, rng.gauss(82, 30))
        score = (
            -1.25
            - 0.035 * tenure
            + 0.018 * monthly
            + 0.32 * tickets
            + 0.48 * late
            + 0.006 * usage
            + (0.86 if contract == "Month-to-month" else -0.22 if contract == "Two year" else 0.0)
        )
        churn_probability = sigmoid(score)
        churn = 1 if rng.random() < churn_probability else 0
        rows.append({
            "customer_id": f"CUST-{index:04d}",
            "tenure_months": tenure,
            "monthly_charges": f"{monthly:.2f}",
            "support_tickets": tickets,
            "late_payments": late,
            "usage_gb": f"{usage:.2f}",
            "contract_type": contract,
            "churn": churn,
        })

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def feature_vector(row: dict[str, str]) -> list[float]:
    contract = row["contract_type"]
    return [
        float(row["tenure_months"]),
        float(row["monthly_charges"]),
        float(row["support_tickets"]),
        float(row["late_payments"]),
        float(row["usage_gb"]),
        1.0 if contract == "Month-to-month" else 0.0,
        1.0 if contract == "One year" else 0.0,
        1.0 if contract == "Two year" else 0.0,
    ]


def standardize(train: list[list[float]], rows: list[list[float]]) -> tuple[list[list[float]], list[float], list[float]]:
    columns = list(zip(*train))
    means = [sum(column) / len(column) for column in columns]
    scales = []
    for column, center in zip(columns, means):
        variance = sum((value - center) ** 2 for value in column) / len(column)
        scales.append(math.sqrt(variance) or 1.0)
    transformed = [[(value - means[index]) / scales[index] for index, value in enumerate(row)] for row in rows]
    return transformed, means, scales


def apply_standardization(rows: list[list[float]], means: list[float], scales: list[float]) -> list[list[float]]:
    return [[(value - means[index]) / scales[index] for index, value in enumerate(row)] for row in rows]


def train_logistic_regression(features: list[list[float]], labels: list[int], epochs: int = 1200, lr: float = 0.08) -> list[float]:
    weights = [0.0 for _ in range(len(features[0]) + 1)]
    for _ in range(epochs):
        gradients = [0.0 for _ in weights]
        for row, label in zip(features, labels):
            x = [1.0] + row
            probability = sigmoid(sum(weight * value for weight, value in zip(weights, x)))
            error = probability - label
            for index, value in enumerate(x):
                gradients[index] += error * value
        for index in range(len(weights)):
            weights[index] -= lr * gradients[index] / len(features)
    return weights


def predict_probability(weights: list[float], row: list[float]) -> float:
    x = [1.0] + row
    return sigmoid(sum(weight * value for weight, value in zip(weights, x)))


def metrics(labels: list[int], probabilities: list[float]) -> dict[str, float]:
    predictions = [1 if value >= 0.5 else 0 for value in probabilities]
    tp = sum(1 for truth, pred in zip(labels, predictions) if truth == 1 and pred == 1)
    tn = sum(1 for truth, pred in zip(labels, predictions) if truth == 0 and pred == 0)
    fp = sum(1 for truth, pred in zip(labels, predictions) if truth == 0 and pred == 1)
    fn = sum(1 for truth, pred in zip(labels, predictions) if truth == 1 and pred == 0)
    accuracy = (tp + tn) / len(labels)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"accuracy": accuracy, "precision": precision, "recall": recall, "f1": f1, "auc": auc(labels, probabilities)}


def auc(labels: list[int], probabilities: list[float]) -> float:
    pairs = sorted(zip(probabilities, labels), key=lambda item: item[0])
    positives = sum(labels)
    negatives = len(labels) - positives
    if positives == 0 or negatives == 0:
        return 0.0
    rank_sum = sum(rank for rank, (_, label) in enumerate(pairs, start=1) if label == 1)
    return (rank_sum - positives * (positives + 1) / 2) / (positives * negatives)


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def churn_by_contract(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    output = []
    for contract in sorted({row["contract_type"] for row in rows}):
        group = [row for row in rows if row["contract_type"] == contract]
        rate = sum(int(row["churn"]) for row in group) / len(group)
        output.append({"contract_type": contract, "customers": len(group), "churn_rate": round(rate, 3)})
    return output


def forecast_churn(scored_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    base_expected = sum(float(row["churn_probability"]) for row in scored_rows)
    output = []
    for month in range(1, 7):
        retention_program_effect = 1 - min(0.18, month * 0.025)
        expected_churn = base_expected * retention_program_effect / 6
        output.append({
            "forecast_month": f"Month {month}",
            "expected_churned_customers": round(expected_churn, 1),
            "retention_program_effect": round(1 - retention_program_effect, 3),
        })
    return output


def write_preview_svg(path: Path, model_metrics: dict[str, float], forecast: list[dict[str, object]]) -> None:
    width, height = 1200, 750
    values = [model_metrics["accuracy"], model_metrics["precision"], model_metrics["recall"], model_metrics["f1"], model_metrics["auc"]]
    labels = ["Accuracy", "Precision", "Recall", "F1", "AUC"]
    max_forecast = max(float(row["expected_churned_customers"]) for row in forecast)
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 750" role="img" aria-label="Churn model evaluation and forecast preview">',
        '<rect width="1200" height="750" rx="42" fill="#eef2ff"/>',
        '<rect x="70" y="70" width="1060" height="610" rx="30" fill="#ffffff"/>',
        '<text x="110" y="135" font-family="Arial" font-size="36" font-weight="800" fill="#0f172a">Customer Churn ML and Forecasting</text>',
        '<text x="110" y="172" font-family="Arial" font-size="22" fill="#475569">Model evaluation, churn scoring, and six-month forecast</text>',
        '<rect x="110" y="230" width="520" height="370" rx="24" fill="#f8fafc"/>',
        '<text x="145" y="282" font-family="Arial" font-size="24" font-weight="700" fill="#0f172a">Evaluation Metrics</text>',
    ]
    for index, (label, value) in enumerate(zip(labels, values)):
        y = 325 + index * 48
        svg.append(f'<text x="145" y="{y}" font-family="Arial" font-size="20" fill="#475569">{label}</text>')
        svg.append(f'<rect x="280" y="{y - 22}" width="{value * 260:.1f}" height="24" rx="12" fill="#2563eb"/>')
        svg.append(f'<text x="560" y="{y}" font-family="Arial" font-size="20" font-weight="700" fill="#0f172a">{value:.2f}</text>')
    svg.append('<rect x="675" y="230" width="405" height="370" rx="24" fill="#f8fafc"/>')
    svg.append('<text x="710" y="282" font-family="Arial" font-size="24" font-weight="700" fill="#0f172a">Forecast</text>')
    last_x, last_y = None, None
    for index, row in enumerate(forecast):
        x = 725 + index * 58
        y = 550 - float(row["expected_churned_customers"]) / max_forecast * 210
        svg.append(f'<circle cx="{x}" cy="{y:.1f}" r="9" fill="#14b8a6"/>')
        if last_x is not None:
            svg.append(f'<line x1="{last_x}" y1="{last_y:.1f}" x2="{x}" y2="{y:.1f}" stroke="#14b8a6" stroke-width="5"/>')
        last_x, last_y = x, y
    svg.append("</svg>")
    path.write_text("\n".join(svg), encoding="utf-8")


def write_report(path: Path, rows: list[dict[str, str]], model_metrics: dict[str, float], contract_rates: list[dict[str, object]], forecast: list[dict[str, object]]) -> None:
    churn_rate = sum(int(row["churn"]) for row in rows) / len(rows)
    report = f"""# Customer Churn Machine Learning and Forecasting Report

## Project Question

Which customers are most likely to churn, and how many churn events should the business expect over the next six months?

## Exploratory Data Analysis

- Customers analyzed: {len(rows)}
- Overall churn rate: {churn_rate:.1%}
- Highest-risk segment is visible through contract-level churn rates.

| Contract type | Customers | Churn rate |
| --- | --- | --- |
{chr(10).join(f"| {row['contract_type']} | {row['customers']} | {float(row['churn_rate']):.1%} |" for row in contract_rates)}

## Model Evaluation

| Metric | Value |
| --- | --- |
| Accuracy | {model_metrics['accuracy']:.3f} |
| Precision | {model_metrics['precision']:.3f} |
| Recall | {model_metrics['recall']:.3f} |
| F1 score | {model_metrics['f1']:.3f} |
| ROC AUC | {model_metrics['auc']:.3f} |

## Forecast

| Month | Expected churned customers | Retention program effect |
| --- | --- | --- |
{chr(10).join(f"| {row['forecast_month']} | {row['expected_churned_customers']} | {float(row['retention_program_effect']):.1%} |" for row in forecast)}

## Portfolio Interpretation

The project demonstrates EDA, supervised machine learning, model evaluation, churn scoring, and practical forecasting. It is ready to be extended with Pandas, NumPy, scikit-learn, and notebook visuals.
"""
    path.write_text(report, encoding="utf-8")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ASSET_DIR.mkdir(parents=True, exist_ok=True)

    data_path = DATA_DIR / "customer_churn.csv"
    generate_dataset(data_path)
    rows = read_rows(data_path)
    rng = random.Random(515)
    rng.shuffle(rows)

    features = [feature_vector(row) for row in rows]
    labels = [int(row["churn"]) for row in rows]
    split = int(len(rows) * 0.75)
    train_features_raw = features[:split]
    test_features_raw = features[split:]
    train_labels = labels[:split]
    test_labels = labels[split:]

    train_features, means, scales = standardize(train_features_raw, train_features_raw)
    test_features = apply_standardization(test_features_raw, means, scales)
    weights = train_logistic_regression(train_features, train_labels)
    test_probabilities = [predict_probability(weights, row) for row in test_features]
    model_metrics = metrics(test_labels, test_probabilities)

    all_features = apply_standardization(features, means, scales)
    all_scores = [predict_probability(weights, row) for row in all_features]
    scored_rows = []
    for row, probability in zip(rows, all_scores):
        scored = dict(row)
        scored["churn_probability"] = round(probability, 4)
        scored["risk_band"] = "High" if probability >= 0.65 else "Medium" if probability >= 0.4 else "Low"
        scored_rows.append(scored)
    score_fields = list(scored_rows[0].keys())
    write_csv(OUTPUT_DIR / "churn_scores.csv", scored_rows, score_fields)

    contract_rates = churn_by_contract(rows)
    forecast = forecast_churn(scored_rows)
    write_csv(OUTPUT_DIR / "forecast.csv", forecast, ["forecast_month", "expected_churned_customers", "retention_program_effect"])
    write_report(OUTPUT_DIR / "model_evaluation.md", rows, model_metrics, contract_rates, forecast)
    write_preview_svg(ASSET_DIR / "churn_forecasting_preview.svg", model_metrics, forecast)
    print("Customer churn ML and forecasting project generated.")


if __name__ == "__main__":
    main()
