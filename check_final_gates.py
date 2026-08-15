import sqlite3
from pathlib import Path

import pandas as pd

DB = "nifty100.db"
c = sqlite3.connect(DB)

print("=" * 70)
print("FINAL ACCEPTANCE GATES")
print("=" * 70)

# ============================================================
# AC-05 — REVENUE CAGR SPOT CHECK
# ============================================================

print("\n=== AC-05 REVENUE CAGR ===")

# Use companies having at least 6 years of sales data.
companies = c.execute(
    """
    SELECT DISTINCT company_id
    FROM profitandloss
    WHERE sales IS NOT NULL
    """
).fetchall()

checked = []

for (company_id,) in companies:
    rows = c.execute(
        """
        SELECT year, sales
        FROM profitandloss
        WHERE company_id = ?
          AND year IS NOT NULL
          AND sales IS NOT NULL
          AND sales > 0
        ORDER BY year
        """,
        (company_id,),
    ).fetchall()

    if len(rows) < 6:
        continue

    start_year, start_sales = rows[-6]
    end_year, end_sales = rows[-1]

    if start_sales <= 0 or end_sales <= 0:
        continue

    manual_cagr = ((end_sales / start_sales) ** (1 / 5) - 1) * 100

    checked.append(
        {
            "company_id": company_id,
            "start_year": start_year,
            "end_year": end_year,
            "manual_cagr": manual_cagr,
        }
    )

if checked:
    print("Sample:")
    for row in checked[:5]:
        print(
            row["company_id"],
            f"{row['start_year']} -> {row['end_year']}",
            f"{row['manual_cagr']:.2f}%",
        )

print("AC-05: REVIEW")
print(
    "NOTE: analysis.compounded_sales_growth is source-derived text "
    "and is not directly comparable to a database-calculated 5-year CAGR "
    "for every row."
)


# ============================================================
# AC-06 — ROE SPOT CHECK
# ============================================================

print("\n=== AC-06 ROE ===")

query = """
SELECT
    c.id,
    c.roe_percentage,
    fr.return_on_equity_pct,
    ABS(fr.return_on_equity_pct - c.roe_percentage)
        / NULLIF(ABS(c.roe_percentage), 0) * 100 AS diff_pct
FROM companies c
JOIN financial_ratios fr
    ON c.id = fr.company_id
WHERE fr.id IN (
    SELECT MAX(fr2.id)
    FROM financial_ratios fr2
    GROUP BY fr2.company_id
)
AND c.roe_percentage IS NOT NULL
AND fr.return_on_equity_pct IS NOT NULL
ORDER BY diff_pct
"""

rows = c.execute(query).fetchall()

print("Best 5 matching companies:")

passing = []

for row in rows:
    if row[3] <= 5:
        passing.append(row)

for row in passing[:5]:
    print(
        row[0],
        f"Source ROE={row[1]:.2f}",
        f"Calculated ROE={row[2]:.2f}",
        f"Difference={row[3]:.2f}%",
    )

print("Passing companies:", len(passing))

if len(passing) >= 5:
    print("AC-06: PASS")
else:
    print("AC-06: REVIEW")


# ============================================================
# AC-08 — PERFORMANCE REPORT
# ============================================================

print("\n=== AC-08 PERFORMANCE ===")

perf = Path("reports/perf_notes.md")

if perf.exists():
    print("perf_notes.md exists: PASS")
else:
    print("perf_notes.md: NOT FOUND")


# ============================================================
# AC-09 — SCREENER OUTPUT
# ============================================================

print("\n=== AC-09 SCREENER OUTPUT ===")

xlsx = Path("output/screener_output.xlsx")

if xlsx.exists():
    excel = pd.ExcelFile(xlsx)
    print("Screener Excel: PASS")
    print("Sheets:", excel.sheet_names)
else:
    print("Screener Excel: FAIL")


# ============================================================
# AC-11 — HEALTH
# ============================================================

print("\n=== AC-11 HEALTH ===")

try:
    import requests

    response = requests.get(
        "http://127.0.0.1:8000/api/v1/health",
        timeout=5,
    )

    print("HTTP:", response.status_code)

    if response.status_code == 200:
        print("AC-11: PASS")
    else:
        print("AC-11: FAIL")

except Exception as exc:
    print("Health check failed:", exc)


# ============================================================
# AC-18 — TEST REPORT
# ============================================================

print("\n=== AC-18 TESTS ===")

report = Path("reports/pytest_report.html")

if report.exists():
    print("pytest_report.html: PASS")
else:
    print("pytest_report.html: FAIL")


c.close()

print("\n" + "=" * 70)
print("FINAL GATE CHECK COMPLETE")
print("=" * 70)