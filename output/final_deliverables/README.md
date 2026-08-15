# N100 Financial Intelligence Platform

## Overview

The N100 Financial Intelligence Platform is an interactive financial analytics system built using Python, Streamlit, SQLite, FastAPI, Pandas, NumPy, and Plotly.

The platform analyzes companies in the Nifty 100 universe using financial statements, financial ratios, valuation metrics, peer comparison, sector analysis, portfolio statistics, clustering, and stock screening.

The project includes an ETL pipeline, data-quality validation, financial KPI calculations, analytics modules, a Streamlit dashboard, a FastAPI service, automated tests, performance tests, and generated analyst reports.

---

## Features

- Interactive Streamlit Dashboard
- Company Profile
- Financial Screener
- Peer Comparison
- Trend Analysis
- Sector Analysis
- Capital Structure Analysis
- Annual Reports / Tear Sheets
- Valuation Analytics
- Financial Ratio Engine
- Cash Flow Intelligence
- K-Means Company Clustering
- Correlation Analysis
- Data Quality Validation
- FastAPI REST API
- Automated Test Suite
- API Load Testing
- Dashboard Performance Testing

---

## Technology Stack

- Python 3.11
- Pandas
- NumPy
- SQLite
- Streamlit
- FastAPI
- Uvicorn
- Plotly
- Matplotlib
- Seaborn
- Scikit-learn
- PyYAML
- ReportLab
- pytest
- pytest-html
- Black
- Ruff

---

## Project Structure

```text
n100-financial-platform/
│
├── data/
│
├── docs/
│   ├── analyst_guide.pdf
│   ├── openapi.json
│   └── perf_notes.md
│
├── output/
│   ├── cluster_labels.csv
│   ├── cluster_mean_stats.csv
│   ├── cluster_median_stats.csv
│   ├── portfolio_stats.csv
│   ├── outlier_report.csv
│   └── ...
│
├── reports/
│   ├── elbow_plot.png
│   ├── correlation_heatmap.png
│   ├── pytest_report.html
│   └── tearsheets/
│
├── src/
│   ├── analytics/
│   ├── api/
│   ├── dashboard/
│   ├── etl/
│   ├── nlp/
│   ├── reports/
│   └── screener/
│
├── tests/
│   ├── api/
│   ├── dq/
│   ├── etl/
│   ├── kpi/
│   └── performance/
│
├── nifty100.db
├── README.md
└── requirements.txt