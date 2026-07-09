from __future__ import annotations

import csv
import math
import random
import sqlite3
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
OUTPUT_DIR = ROOT / "output"
EXPORT_DIR = OUTPUT_DIR / "powerbi_tableau_exports"
DASHBOARD_DIR = ROOT / "dashboard"
ASSET_DIR = ROOT / "assets"


PRODUCTS = [
    {"product": "Wireless Mouse", "category": "Accessories", "price": 22.0, "cost": 11.5},
    {"product": "Mechanical Keyboard", "category": "Accessories", "price": 78.0, "cost": 42.0},
    {"product": "USB-C Hub", "category": "Accessories", "price": 45.0, "cost": 24.0},
    {"product": "Noise Cancel Headset", "category": "Audio", "price": 128.0, "cost": 72.0},
    {"product": "Bluetooth Speaker", "category": "Audio", "price": 58.0, "cost": 29.0},
    {"product": "Fitness Band", "category": "Wearables", "price": 65.0, "cost": 31.0},
    {"product": "Smart Watch", "category": "Wearables", "price": 190.0, "cost": 105.0},
    {"product": "Laptop Stand", "category": "Office", "price": 35.0, "cost": 16.0},
    {"product": "Desk Lamp", "category": "Office", "price": 42.0, "cost": 18.0},
]

REGIONS = ["North", "South", "East", "West"]
CHANNELS = ["Online", "Retail", "Partner"]
SEGMENTS = ["Student", "Professional", "Small Business"]


def ensure_dirs() -> None:
    for path in [RAW_DIR, PROCESSED_DIR, OUTPUT_DIR, EXPORT_DIR, DASHBOARD_DIR, ASSET_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def generate_orders(path: Path) -> None:
    if path.exists():
        return

    rng = random.Random(20260709)
    fields = [
        "order_id",
        "order_date",
        "region",
        "channel",
        "customer_segment",
        "product",
        "category",
        "units",
        "unit_price",
        "unit_cost",
        "discount_rate",
        "shipping_cost",
        "status",
    ]
    start = date(2025, 1, 1)
    rows = []
    for index in range(1, 421):
        product = rng.choice(PRODUCTS)
        order_date = start + timedelta(days=rng.randrange(365))
        seasonal_boost = 1.35 if order_date.month in [10, 11, 12] else 1.0
        units = max(1, round(rng.triangular(1, 8, 2) * seasonal_boost))
        discount = rng.choice([0.00, 0.05, 0.10, 0.15])
        status = rng.choices(["Completed", "Returned", "Cancelled"], weights=[88, 8, 4], k=1)[0]
        rows.append({
            "order_id": f"ORD-{index:04d}",
            "order_date": order_date.isoformat(),
            "region": rng.choice(REGIONS),
            "channel": rng.choices(CHANNELS, weights=[50, 34, 16], k=1)[0],
            "customer_segment": rng.choice(SEGMENTS),
            "product": product["product"],
            "category": product["category"],
            "units": units,
            "unit_price": f"{product['price']:.2f}",
            "unit_cost": f"{product['cost']:.2f}",
            "discount_rate": f"{discount:.2f}",
            "shipping_cost": f"{rng.uniform(2.5, 13.5):.2f}",
            "status": status,
        })

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def clean_orders(raw_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    clean = []
    for row in raw_rows:
        if row["status"].strip().lower() != "completed":
            continue

        units = int(float(row["units"]))
        unit_price = float(row["unit_price"])
        unit_cost = float(row["unit_cost"])
        discount_rate = float(row["discount_rate"])
        shipping_cost = float(row["shipping_cost"])
        order_date = date.fromisoformat(row["order_date"])
        gross_sales = units * unit_price
        discount_amount = gross_sales * discount_rate
        revenue = gross_sales - discount_amount
        profit = revenue - (units * unit_cost) - shipping_cost

        clean.append({
            "order_id": row["order_id"],
            "order_date": order_date.isoformat(),
            "month": order_date.strftime("%Y-%m"),
            "region": row["region"].title(),
            "channel": row["channel"].title(),
            "customer_segment": row["customer_segment"].title(),
            "product": row["product"],
            "category": row["category"],
            "units": units,
            "unit_price": round(unit_price, 2),
            "discount_rate": round(discount_rate, 2),
            "revenue": round(revenue, 2),
            "profit": round(profit, 2),
        })
    return clean


def aggregate(rows: list[dict[str, object]], key: str) -> list[dict[str, object]]:
    groups: dict[str, dict[str, float]] = defaultdict(lambda: {"revenue": 0.0, "profit": 0.0, "units": 0.0, "orders": 0.0})
    for row in rows:
        group = groups[str(row[key])]
        group["revenue"] += float(row["revenue"])
        group["profit"] += float(row["profit"])
        group["units"] += float(row["units"])
        group["orders"] += 1
    output = []
    for value, metrics in sorted(groups.items()):
        output.append({
            key: value,
            "revenue": round(metrics["revenue"], 2),
            "profit": round(metrics["profit"], 2),
            "units": int(metrics["units"]),
            "orders": int(metrics["orders"]),
            "avg_order_value": round(metrics["revenue"] / metrics["orders"], 2),
        })
    return output


def write_database(rows: list[dict[str, object]], summaries: dict[str, list[dict[str, object]]]) -> None:
    db_path = OUTPUT_DIR / "retail_analytics.db"
    if db_path.exists():
        db_path.unlink()
    connection = sqlite3.connect(db_path)
    try:
        fields = list(rows[0].keys())
        placeholders = ",".join("?" for _ in fields)
        connection.execute(
            f"CREATE TABLE clean_orders ({','.join(field + ' TEXT' for field in fields)})"
        )
        connection.executemany(
            f"INSERT INTO clean_orders ({','.join(fields)}) VALUES ({placeholders})",
            [[row[field] for field in fields] for row in rows],
        )

        for table_name, table_rows in summaries.items():
            table_fields = list(table_rows[0].keys())
            connection.execute(
                f"CREATE TABLE {table_name} ({','.join(field + ' TEXT' for field in table_fields)})"
            )
            connection.executemany(
                f"INSERT INTO {table_name} ({','.join(table_fields)}) VALUES ({','.join('?' for _ in table_fields)})",
                [[row[field] for field in table_fields] for row in table_rows],
            )
        connection.commit()
    finally:
        connection.close()


def write_excel_xml(path: Path, sheets: dict[str, list[dict[str, object]]]) -> None:
    workbook = ['<?xml version="1.0"?>']
    workbook.append('<?mso-application progid="Excel.Sheet"?>')
    workbook.append('<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet" xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">')
    for sheet_name, rows in sheets.items():
        workbook.append(f'<Worksheet ss:Name="{escape(sheet_name[:31])}"><Table>')
        headers = list(rows[0].keys())
        workbook.append("<Row>" + "".join(f'<Cell><Data ss:Type="String">{escape(header)}</Data></Cell>' for header in headers) + "</Row>")
        for row in rows:
            workbook.append("<Row>")
            for header in headers:
                value = row[header]
                data_type = "Number" if isinstance(value, (int, float)) else "String"
                workbook.append(f'<Cell><Data ss:Type="{data_type}">{escape(str(value))}</Data></Cell>')
            workbook.append("</Row>")
        workbook.append("</Table></Worksheet>")
    workbook.append("</Workbook>")
    path.write_text("\n".join(workbook), encoding="utf-8")


def write_preview_svg(path: Path, monthly: list[dict[str, object]], category: list[dict[str, object]]) -> None:
    width, height = 1200, 750
    max_revenue = max(float(row["revenue"]) for row in monthly)
    bar_width = 700 / len(monthly)
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="Retail analytics dashboard preview">',
        '<rect width="1200" height="750" rx="42" fill="#eef7ff"/>',
        '<rect x="70" y="70" width="1060" height="610" rx="30" fill="#ffffff"/>',
        '<text x="110" y="135" font-family="Arial" font-size="36" font-weight="800" fill="#0f172a">Retail Sales Analytics Dashboard</text>',
        '<text x="110" y="172" font-family="Arial" font-size="22" fill="#475569">Python cleaning, SQL metrics, Excel and BI exports</text>',
    ]
    total_revenue = sum(float(row["revenue"]) for row in monthly)
    total_profit = sum(float(row["profit"]) for row in monthly)
    for i, (label, value) in enumerate([("Revenue", total_revenue), ("Profit", total_profit), ("Orders", sum(int(row["orders"]) for row in monthly))]):
        x = 110 + i * 300
        svg.append(f'<rect x="{x}" y="210" width="250" height="120" rx="20" fill="#f8fafc"/>')
        svg.append(f'<text x="{x + 24}" y="255" font-family="Arial" font-size="22" fill="#475569">{label}</text>')
        svg.append(f'<text x="{x + 24}" y="300" font-family="Arial" font-size="34" font-weight="800" fill="#2563eb">{value:,.0f}</text>')
    svg.append('<rect x="110" y="390" width="760" height="210" rx="22" fill="#f8fafc"/>')
    for index, row in enumerate(monthly):
        x = 140 + index * bar_width
        h = float(row["revenue"]) / max_revenue * 150
        y = 570 - h
        svg.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width - 10:.1f}" height="{h:.1f}" rx="8" fill="#14b8a6"/>')
    svg.append('<text x="140" y="635" font-family="Arial" font-size="22" font-weight="700" fill="#0f172a">Monthly revenue trend</text>')
    svg.append('<rect x="900" y="390" width="180" height="210" rx="22" fill="#f8fafc"/>')
    for index, row in enumerate(sorted(category, key=lambda item: float(item["revenue"]), reverse=True)[:4]):
        y = 435 + index * 38
        svg.append(f'<circle cx="930" cy="{y}" r="10" fill="#2563eb"/>')
        svg.append(f'<text x="950" y="{y + 7}" font-family="Arial" font-size="20" fill="#0f172a">{escape(str(row["category"]))}</text>')
    svg.append("</svg>")
    path.write_text("\n".join(svg), encoding="utf-8")


def write_dashboard_html(path: Path, monthly: list[dict[str, object]], category: list[dict[str, object]], region: list[dict[str, object]]) -> None:
    cards = {
        "Revenue": sum(float(row["revenue"]) for row in monthly),
        "Profit": sum(float(row["profit"]) for row in monthly),
        "Orders": sum(int(row["orders"]) for row in monthly),
        "AOV": sum(float(row["revenue"]) for row in monthly) / sum(int(row["orders"]) for row in monthly),
    }
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Retail Sales Analytics Dashboard</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; background: #f6f8fc; color: #0f172a; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 40px 20px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }}
    .card {{ background: white; border: 1px solid #e2e8f0; border-radius: 14px; padding: 20px; box-shadow: 0 8px 28px rgba(15, 23, 42, .06); }}
    .metric {{ font-size: 32px; font-weight: 800; color: #2563eb; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ padding: 10px; border-bottom: 1px solid #e2e8f0; text-align: left; }}
  </style>
</head>
<body>
  <main>
    <h1>Retail Sales Analytics Dashboard</h1>
    <p>Cleaned sales data with Python, modeled through SQL, exported for Excel, Power BI, and Tableau.</p>
    <section class="grid">
      <div class="card"><span>Revenue</span><div class="metric">${cards['Revenue']:,.0f}</div></div>
      <div class="card"><span>Profit</span><div class="metric">${cards['Profit']:,.0f}</div></div>
      <div class="card"><span>Orders</span><div class="metric">{cards['Orders']:,.0f}</div></div>
      <div class="card"><span>Average Order Value</span><div class="metric">${cards['AOV']:,.0f}</div></div>
    </section>
    <section class="grid" style="margin-top: 20px;">
      <div class="card">
        <h2>Top Categories</h2>
        <table><tr><th>Category</th><th>Revenue</th><th>Profit</th></tr>
          {''.join(f"<tr><td>{row['category']}</td><td>${float(row['revenue']):,.0f}</td><td>${float(row['profit']):,.0f}</td></tr>" for row in sorted(category, key=lambda item: float(item['revenue']), reverse=True))}
        </table>
      </div>
      <div class="card">
        <h2>Regions</h2>
        <table><tr><th>Region</th><th>Revenue</th><th>AOV</th></tr>
          {''.join(f"<tr><td>{row['region']}</td><td>${float(row['revenue']):,.0f}</td><td>${float(row['avg_order_value']):,.0f}</td></tr>" for row in sorted(region, key=lambda item: float(item['revenue']), reverse=True))}
        </table>
      </div>
    </section>
  </main>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")


def write_report(rows: list[dict[str, object]], monthly: list[dict[str, object]], category: list[dict[str, object]], region: list[dict[str, object]]) -> None:
    revenue = sum(float(row["revenue"]) for row in rows)
    profit = sum(float(row["profit"]) for row in rows)
    best_category = max(category, key=lambda row: float(row["revenue"]))
    best_region = max(region, key=lambda row: float(row["revenue"]))
    report = f"""# Retail Sales Analytics Dashboard Report

## Executive Summary

The cleaned dataset contains {len(rows)} completed retail orders. Total revenue is ${revenue:,.2f}, total profit is ${profit:,.2f}, and the strongest category is {best_category['category']}.

## Data Cleaning

- Removed cancelled and returned orders from KPI calculations.
- Standardized date, region, channel, and customer segment fields.
- Created revenue, profit, month, and average order value metrics.
- Exported clean tables for Excel, Power BI, and Tableau.

## Dashboard Findings

- Best category by revenue: {best_category['category']} (${float(best_category['revenue']):,.2f}).
- Best region by revenue: {best_region['region']} (${float(best_region['revenue']):,.2f}).
- Average order value: ${revenue / len(rows):,.2f}.

## Files for Portfolio Review

- `dashboard/index.html`
- `output/retail_analytics.db`
- `output/excel_dashboard_workbook.xml`
- `output/powerbi_tableau_exports/`
"""
    (OUTPUT_DIR / "report.md").write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    raw_path = RAW_DIR / "orders.csv"
    generate_orders(raw_path)
    rows = clean_orders(read_csv(raw_path))
    clean_fields = list(rows[0].keys())
    write_csv(PROCESSED_DIR / "clean_orders.csv", rows, clean_fields)

    summaries = {
        "monthly_sales": aggregate(rows, "month"),
        "category_sales": aggregate(rows, "category"),
        "region_sales": aggregate(rows, "region"),
        "channel_sales": aggregate(rows, "channel"),
    }
    for name, table_rows in summaries.items():
        write_csv(EXPORT_DIR / f"{name}.csv", table_rows, list(table_rows[0].keys()))
    write_database(rows, summaries)
    write_excel_xml(OUTPUT_DIR / "excel_dashboard_workbook.xml", {"Clean Orders": rows[:200], **summaries})
    write_preview_svg(ASSET_DIR / "retail_dashboard_preview.svg", summaries["monthly_sales"], summaries["category_sales"])
    write_dashboard_html(DASHBOARD_DIR / "index.html", summaries["monthly_sales"], summaries["category_sales"], summaries["region_sales"])
    write_report(rows, summaries["monthly_sales"], summaries["category_sales"], summaries["region_sales"])
    print("Retail analytics dashboard project generated.")


if __name__ == "__main__":
    main()
