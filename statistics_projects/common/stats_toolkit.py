from __future__ import annotations

import csv
import math
import random
from html import escape
from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen
from zipfile import ZipFile


USER_AGENT = "Umar-Farooq-Statistics-Portfolio/1.0"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def download_bytes(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        return response.read()


def download_zip(url: str, cache_path: Path) -> ZipFile:
    ensure_dir(cache_path.parent)
    if not cache_path.exists():
        cache_path.write_bytes(download_bytes(url))
    return ZipFile(BytesIO(cache_path.read_bytes()))


def read_csv(path: Path, delimiter: str = ",") -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def numbers(values) -> list[float]:
    return [float(value) for value in values if value is not None and value != ""]


def mean(values: list[float]) -> float:
    if not values:
        raise ValueError("mean requires at least one value")
    return sum(values) / len(values)


def median(values: list[float]) -> float:
    ordered = sorted(values)
    size = len(ordered)
    if size == 0:
        raise ValueError("median requires at least one value")
    midpoint = size // 2
    if size % 2:
        return ordered[midpoint]
    return (ordered[midpoint - 1] + ordered[midpoint]) / 2


def variance(values: list[float], sample: bool = True) -> float:
    if len(values) < 2:
        return 0.0
    center = mean(values)
    denominator = len(values) - 1 if sample else len(values)
    return sum((value - center) ** 2 for value in values) / denominator


def stdev(values: list[float], sample: bool = True) -> float:
    return math.sqrt(variance(values, sample=sample))


def percentile(values: list[float], p: float) -> float:
    if not values:
        raise ValueError("percentile requires at least one value")
    if p <= 0:
        return min(values)
    if p >= 1:
        return max(values)
    ordered = sorted(values)
    rank = (len(ordered) - 1) * p
    low = math.floor(rank)
    high = math.ceil(rank)
    if low == high:
        return ordered[int(rank)]
    weight = rank - low
    return ordered[low] * (1 - weight) + ordered[high] * weight


def summarize(values: list[float]) -> dict[str, float]:
    clean = numbers(values)
    return {
        "n": len(clean),
        "mean": mean(clean),
        "median": median(clean),
        "sd": stdev(clean),
        "min": min(clean),
        "q1": percentile(clean, 0.25),
        "q3": percentile(clean, 0.75),
        "max": max(clean),
    }


def proportion(rows: list[object], predicate) -> float:
    if not rows:
        return 0.0
    return sum(1 for row in rows if predicate(row)) / len(rows)


def pearson(x_values: list[float], y_values: list[float]) -> float:
    x_center = mean(x_values)
    y_center = mean(y_values)
    numerator = sum((x - x_center) * (y - y_center) for x, y in zip(x_values, y_values))
    x_denominator = math.sqrt(sum((x - x_center) ** 2 for x in x_values))
    y_denominator = math.sqrt(sum((y - y_center) ** 2 for y in y_values))
    if x_denominator == 0 or y_denominator == 0:
        return 0.0
    return numerator / (x_denominator * y_denominator)


def simple_linear_regression(x_values: list[float], y_values: list[float]) -> dict[str, float]:
    x_center = mean(x_values)
    y_center = mean(y_values)
    ss_x = sum((x - x_center) ** 2 for x in x_values)
    if ss_x == 0:
        raise ValueError("simple regression requires variation in x")
    slope = sum((x - x_center) * (y - y_center) for x, y in zip(x_values, y_values)) / ss_x
    intercept = y_center - slope * x_center
    predictions = [intercept + slope * x for x in x_values]
    residuals = [y - prediction for y, prediction in zip(y_values, predictions)]
    sse = sum(residual ** 2 for residual in residuals)
    sst = sum((y - y_center) ** 2 for y in y_values)
    r2 = 1 - sse / sst if sst else 0.0
    rmse = math.sqrt(sse / len(y_values))
    return {
        "intercept": intercept,
        "slope": slope,
        "r": pearson(x_values, y_values),
        "r2": r2,
        "rmse": rmse,
    }


def transpose(matrix: list[list[float]]) -> list[list[float]]:
    return [list(column) for column in zip(*matrix)]


def matmul(left: list[list[float]], right: list[list[float]]) -> list[list[float]]:
    return [
        [sum(a * b for a, b in zip(row, column)) for column in transpose(right)]
        for row in left
    ]


def invert_matrix(matrix: list[list[float]]) -> list[list[float]]:
    size = len(matrix)
    augmented = [
        row[:] + [1.0 if i == j else 0.0 for j in range(size)]
        for i, row in enumerate(matrix)
    ]

    for col in range(size):
        pivot = max(range(col, size), key=lambda row: abs(augmented[row][col]))
        if abs(augmented[pivot][col]) < 1e-12:
            raise ValueError("matrix is singular")
        if pivot != col:
            augmented[col], augmented[pivot] = augmented[pivot], augmented[col]

        divisor = augmented[col][col]
        augmented[col] = [value / divisor for value in augmented[col]]

        for row in range(size):
            if row == col:
                continue
            factor = augmented[row][col]
            augmented[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(augmented[row], augmented[col])
            ]

    return [row[size:] for row in augmented]


def multiple_linear_regression(
    features: list[list[float]],
    target: list[float],
    feature_names: list[str],
) -> dict[str, object]:
    design = [[1.0] + row for row in features]
    y_column = [[value] for value in target]
    xt = transpose(design)
    xtx = matmul(xt, design)
    xtx_inv = invert_matrix(xtx)
    xty = matmul(xt, y_column)
    beta = [row[0] for row in matmul(xtx_inv, xty)]
    predictions = [sum(coef * value for coef, value in zip(beta, row)) for row in design]
    residuals = [actual - predicted for actual, predicted in zip(target, predictions)]
    y_mean = mean(target)
    sse = sum(residual ** 2 for residual in residuals)
    sst = sum((actual - y_mean) ** 2 for actual in target)
    r2 = 1 - sse / sst if sst else 0.0
    rmse = math.sqrt(sse / len(target))
    return {
        "coefficients": dict(zip(["intercept"] + feature_names, beta)),
        "predictions": predictions,
        "residuals": residuals,
        "r2": r2,
        "rmse": rmse,
        "n": len(target),
    }


def bootstrap_ci(
    values: list[float],
    statistic,
    iterations: int = 3000,
    confidence: float = 0.95,
    seed: int = 42,
) -> tuple[float, float]:
    rng = random.Random(seed)
    stats = []
    size = len(values)
    for _ in range(iterations):
        sample = [values[rng.randrange(size)] for _ in range(size)]
        stats.append(statistic(sample))
    alpha = (1 - confidence) / 2
    return percentile(stats, alpha), percentile(stats, 1 - alpha)


def bootstrap_pair_ci(
    x_values: list[float],
    y_values: list[float],
    statistic,
    iterations: int = 3000,
    confidence: float = 0.95,
    seed: int = 42,
) -> tuple[float, float]:
    rng = random.Random(seed)
    pairs = list(zip(x_values, y_values))
    stats = []
    size = len(pairs)
    for _ in range(iterations):
        sample = [pairs[rng.randrange(size)] for _ in range(size)]
        xs = [x for x, _ in sample]
        ys = [y for _, y in sample]
        stats.append(statistic(xs, ys))
    alpha = (1 - confidence) / 2
    return percentile(stats, alpha), percentile(stats, 1 - alpha)


def permutation_mean_difference(
    first: list[float],
    second: list[float],
    iterations: int = 5000,
    seed: int = 42,
) -> dict[str, float]:
    rng = random.Random(seed)
    observed = mean(first) - mean(second)
    combined = first + second
    first_size = len(first)
    extreme = 0
    for _ in range(iterations):
        shuffled = combined[:]
        rng.shuffle(shuffled)
        simulated = mean(shuffled[:first_size]) - mean(shuffled[first_size:])
        if abs(simulated) >= abs(observed):
            extreme += 1
    return {"difference": observed, "p_value": (extreme + 1) / (iterations + 1)}


def permutation_regression_slope(
    x_values: list[float],
    y_values: list[float],
    iterations: int = 5000,
    seed: int = 42,
    alternative: str = "two-sided",
) -> dict[str, float]:
    rng = random.Random(seed)
    observed = simple_linear_regression(x_values, y_values)["slope"]
    extreme = 0
    for _ in range(iterations):
        shuffled = y_values[:]
        rng.shuffle(shuffled)
        simulated = simple_linear_regression(x_values, shuffled)["slope"]
        if alternative == "greater":
            if simulated >= observed:
                extreme += 1
        elif alternative == "less":
            if simulated <= observed:
                extreme += 1
        else:
            if abs(simulated) >= abs(observed):
                extreme += 1
    return {"slope": observed, "p_value": (extreme + 1) / (iterations + 1)}


def fmt(value: float, digits: int = 3) -> str:
    if isinstance(value, int):
        return str(value)
    if abs(value) >= 100:
        return f"{value:.1f}"
    if abs(value) >= 10:
        return f"{value:.2f}"
    return f"{value:.{digits}f}"


def markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(item) for item in row) + " |")
    return "\n".join(lines)


def summary_rows(named_values: dict[str, list[float]]) -> list[list[str]]:
    rows = []
    for label, values in named_values.items():
        stats = summarize(values)
        rows.append([
            label,
            str(stats["n"]),
            fmt(stats["mean"]),
            fmt(stats["median"]),
            fmt(stats["sd"]),
            fmt(stats["min"]),
            fmt(stats["q1"]),
            fmt(stats["q3"]),
            fmt(stats["max"]),
        ])
    return rows


def _scale(value: float, data_min: float, data_max: float, pixel_min: float, pixel_max: float) -> float:
    if data_max == data_min:
        return (pixel_min + pixel_max) / 2
    return pixel_min + (value - data_min) / (data_max - data_min) * (pixel_max - pixel_min)


def write_histogram_svg(path: Path, values: list[float], title: str, x_label: str, bins: int = 10) -> None:
    ensure_dir(path.parent)
    width, height = 1200, 750
    left, right, top, bottom = 110, 70, 110, 120
    min_value, max_value = min(values), max(values)
    if min_value == max_value:
        max_value = min_value + 1
    bin_width = (max_value - min_value) / bins
    counts = [0 for _ in range(bins)]
    for value in values:
        index = min(int((value - min_value) / bin_width), bins - 1)
        counts[index] += 1
    max_count = max(counts)
    plot_width = width - left - right
    plot_height = height - top - bottom
    bar_gap = 8
    bar_width = plot_width / bins - bar_gap
    parts = _svg_start(width, height, title)
    parts.append(_svg_title(title, x_label))
    parts.append(_axis_lines(left, top, width - right, height - bottom))
    for index, count in enumerate(counts):
        x = left + index * (plot_width / bins) + bar_gap / 2
        bar_height = 0 if max_count == 0 else count / max_count * plot_height
        y = height - bottom - bar_height
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{bar_height:.1f}" rx="10" fill="#2563eb"/>')
        if index in (0, bins - 1):
            label = min_value + index * bin_width
            parts.append(_svg_text(x, height - bottom + 34, fmt(label, 1), size=24, anchor="start", fill="#475569"))
    parts.append(_svg_text(width / 2, height - 44, x_label, size=28, anchor="middle", fill="#0f172a", weight=700))
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def write_bar_svg(path: Path, labels: list[str], values: list[float], title: str, y_label: str) -> None:
    ensure_dir(path.parent)
    width, height = 1200, 750
    left, right, top, bottom = 110, 70, 110, 140
    plot_width = width - left - right
    plot_height = height - top - bottom
    max_value = max(values) * 1.1 if values else 1
    bar_gap = 12
    bar_width = plot_width / len(values) - bar_gap
    parts = _svg_start(width, height, title)
    parts.append(_svg_title(title, y_label))
    parts.append(_axis_lines(left, top, width - right, height - bottom))
    for index, (label, value) in enumerate(zip(labels, values)):
        x = left + index * (plot_width / len(values)) + bar_gap / 2
        bar_height = value / max_value * plot_height
        y = height - bottom - bar_height
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{bar_height:.1f}" rx="10" fill="#14b8a6"/>')
        parts.append(_svg_text(x + bar_width / 2, y - 14, fmt(value, 2), size=22, anchor="middle", fill="#0f172a", weight=700))
        parts.append(_svg_text(x + bar_width / 2, height - bottom + 34, escape(str(label)), size=20, anchor="middle", fill="#475569"))
    parts.append(_svg_text(38, height / 2, y_label, size=26, anchor="middle", fill="#0f172a", weight=700, rotate=-90))
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def write_scatter_svg(
    path: Path,
    x_values: list[float],
    y_values: list[float],
    title: str,
    x_label: str,
    y_label: str,
    regression: dict[str, float] | None = None,
) -> None:
    ensure_dir(path.parent)
    width, height = 1200, 750
    left, right, top, bottom = 120, 80, 110, 120
    x_min, x_max = min(x_values), max(x_values)
    y_min, y_max = min(y_values), max(y_values)
    x_pad = (x_max - x_min) * 0.05 or 1
    y_pad = (y_max - y_min) * 0.08 or 1
    x_min -= x_pad
    x_max += x_pad
    y_min -= y_pad
    y_max += y_pad
    parts = _svg_start(width, height, title)
    parts.append(_svg_title(title, f"{x_label} vs {y_label}"))
    parts.append(_axis_lines(left, top, width - right, height - bottom))
    if regression:
        x1, x2 = min(x_values), max(x_values)
        y1 = regression["intercept"] + regression["slope"] * x1
        y2 = regression["intercept"] + regression["slope"] * x2
        px1 = _scale(x1, x_min, x_max, left, width - right)
        px2 = _scale(x2, x_min, x_max, left, width - right)
        py1 = _scale(y1, y_min, y_max, height - bottom, top)
        py2 = _scale(y2, y_min, y_max, height - bottom, top)
        parts.append(f'<line x1="{px1:.1f}" y1="{py1:.1f}" x2="{px2:.1f}" y2="{py2:.1f}" stroke="#ef4444" stroke-width="6" stroke-linecap="round"/>')
    for x, y in zip(x_values, y_values):
        px = _scale(x, x_min, x_max, left, width - right)
        py = _scale(y, y_min, y_max, height - bottom, top)
        parts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="8" fill="#2563eb" opacity="0.68"/>')
    parts.append(_svg_text(width / 2, height - 44, x_label, size=28, anchor="middle", fill="#0f172a", weight=700))
    parts.append(_svg_text(42, height / 2, y_label, size=26, anchor="middle", fill="#0f172a", weight=700, rotate=-90))
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def _svg_start(width: int, height: int, title: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">',
        "<defs>",
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">',
        '<stop offset="0" stop-color="#eef2ff"/>',
        '<stop offset="0.55" stop-color="#f0f9ff"/>',
        '<stop offset="1" stop-color="#dcfce7"/>',
        "</linearGradient>",
        "</defs>",
        f'<rect width="{width}" height="{height}" rx="42" fill="url(#bg)"/>',
        '<rect x="58" y="54" width="1084" height="642" rx="34" fill="#ffffff" opacity="0.92"/>',
    ]


def _svg_title(title: str, subtitle: str) -> str:
    return (
        _svg_text(100, 72, escape(title), size=34, anchor="start", fill="#0f172a", weight=800)
        + "\n"
        + _svg_text(100, 108, escape(subtitle), size=22, anchor="start", fill="#475569")
    )


def _axis_lines(left: int, top: int, right: int, bottom: int) -> str:
    return (
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="#cbd5e1" stroke-width="3"/>'
        f'\n<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="#cbd5e1" stroke-width="3"/>'
    )


def _svg_text(
    x: float,
    y: float,
    text: str,
    size: int,
    anchor: str,
    fill: str,
    weight: int = 500,
    rotate: int | None = None,
) -> str:
    transform = f' transform="rotate({rotate} {x:.1f} {y:.1f})"' if rotate is not None else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" fill="{fill}"'
        f' font-family="Arial, sans-serif" font-size="{size}" font-weight="{weight}"{transform}>{text}</text>'
    )
