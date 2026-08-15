import sqlite3
from pathlib import Path

import pandas as pd
from cashflow_kpis import capital_allocation_pattern

# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "nifty100.db"
OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_DIR.mkdir(exist_ok=True)

CASHFLOW_FILE = OUTPUT_DIR / "cashflow_intelligence.xlsx"
PATTERN_FILE = OUTPUT_DIR / "pattern_changes.csv"


# ==========================================================
# DATABASE
# ==========================================================

conn = sqlite3.connect(DB_PATH)

query = """
SELECT
    company_id,
    year,
    operating_activity,
    investing_activity,
    financing_activity
FROM cashflow
ORDER BY company_id, year
"""

df = pd.read_sql(query, conn)

print("Cashflow rows :", len(df))


# ==========================================================
# CAPITAL ALLOCATION PATTERN
# ==========================================================

df["capital_allocation"] = df.apply(
    lambda row: capital_allocation_pattern(
        row["operating_activity"], row["investing_activity"], row["financing_activity"]
    ),
    axis=1,
)


# ==========================================================
# LATEST YEAR
# ==========================================================

latest_year = df["year"].max()

latest = df[df["year"] == latest_year].copy()

print("Latest year :", latest_year)

print()
print("Capital Allocation Distribution")
print(latest["capital_allocation"].value_counts())


# ==========================================================
# PATTERN CHANGES
# ==========================================================

changes = []

for company, group in df.groupby("company_id"):

    group = group.sort_values("year")

    group["previous_pattern"] = group["capital_allocation"].shift(1)

    changed = group[
        group["previous_pattern"].notna()
        & (group["capital_allocation"] != group["previous_pattern"])
    ]

    for _, row in changed.iterrows():

        changes.append(
            {
                "company_id": company,
                "year": row["year"],
                "previous_pattern": row["previous_pattern"],
                "new_pattern": row["capital_allocation"],
            }
        )


pattern_changes = pd.DataFrame(changes)

if pattern_changes.empty:

    pattern_changes = pd.DataFrame(
        columns=["company_id", "year", "previous_pattern", "new_pattern"]
    )


pattern_changes.to_csv(PATTERN_FILE, index=False)


# ==========================================================
# UPDATE CASH FLOW EXCEL
# ==========================================================

if CASHFLOW_FILE.exists():

    cashflow_df = pd.read_excel(CASHFLOW_FILE)

    # Latest capital allocation pattern for each company
    allocation_latest = latest[["company_id", "capital_allocation"]].copy()

    cashflow_df = cashflow_df.drop(columns=["capital_allocation"], errors="ignore")

    cashflow_df = cashflow_df.merge(allocation_latest, on="company_id", how="left")

    cashflow_df.to_excel(CASHFLOW_FILE, index=False)

    print()
    print("Updated:", CASHFLOW_FILE)

else:

    print()
    print("WARNING: cashflow_intelligence.xlsx not found.")


# ==========================================================
# SUMMARY
# ==========================================================

print()
print("=" * 60)
print("DAY 32 COMPLETED")
print("=" * 60)

print()
print("Latest Year :", latest_year)
print("Companies :", latest["company_id"].nunique())
print("Pattern Changes :", len(pattern_changes))

print()
print("Distribution:")
print(latest["capital_allocation"].value_counts())

print()
print("Generated:")
print(PATTERN_FILE)

conn.close()
