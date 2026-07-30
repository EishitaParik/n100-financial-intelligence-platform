# N100 Financial Intelligence Platform

## Overview

The N100 Financial Intelligence Platform is an interactive financial analytics dashboard built using Python, Streamlit, SQLite, and Plotly.

The platform analyzes companies in the Nifty 100 universe using financial statements, valuation metrics, peer comparison, sector analysis, and stock screening.

---

## Features

- Interactive Dashboard
- Company Profile
- Financial Screener
- Peer Comparison
- Trend Analysis
- Sector Analysis
- Capital Structure Analysis
- Annual Reports
- Valuation Analytics

---

## Technology Stack

- Python
- Streamlit
- SQLite
- Pandas
- Plotly
- NumPy

---

## Project Structure

```
src/
│
├── analytics/
├── dashboard/
├── etl/
├── screener/
└── tests/
```

---

## Dashboard Pages

1. Home
2. Company Profile
3. Screener
4. Peer Comparison
5. Trends
6. Sectors
7. Capital
8. Reports

---

## Outputs

The project generates:

- screener_output.csv
- peer_comparison.xlsx
- valuation_summary.xlsx
- valuation_flags.csv

---

## Run

```bash
streamlit run src/dashboard/app.py
```

---

## Author

Eishita Parik

Bluestock Fintech Internship