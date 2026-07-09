# Retail Sales Analytics Dashboard

Portfolio project for Data Analysis skills: Python, SQL, Excel, Power BI, Tableau, Data Cleaning, and Dashboard Design.

## Project Goal

Build a clean retail analytics workflow that turns raw order records into dashboard-ready outputs for business review.

## What This Project Shows

| Skill | Evidence in this repo |
| --- | --- |
| Python | `src/retail_dashboard_pipeline.py` cleans data, creates metrics, and generates outputs. |
| SQL | `sql/analytics_queries.sql` and the generated SQLite database show reusable business queries. |
| Excel | The pipeline exports an Excel-compatible workbook XML. |
| Power BI | Dashboard-ready CSV exports are written to `output/powerbi_tableau_exports/`. |
| Tableau | The same clean dimensional exports can be loaded directly into Tableau. |
| Data Cleaning | Dates, numeric fields, order status, discount fields, and calculated KPIs are standardized. |
| Dashboard Design | `dashboard/index.html` and `assets/retail_dashboard_preview.svg` show the dashboard layout. |

## Run

```bash
python src/retail_dashboard_pipeline.py
```

## Outputs

- `data/raw/orders.csv`
- `data/processed/clean_orders.csv`
- `output/retail_analytics.db`
- `output/excel_dashboard_workbook.xml`
- `output/powerbi_tableau_exports/*.csv`
- `output/report.md`
- `dashboard/index.html`
- `assets/retail_dashboard_preview.svg`

## Portfolio Summary

This project demonstrates an analyst workflow from messy transactional data to executive-ready dashboard outputs.
