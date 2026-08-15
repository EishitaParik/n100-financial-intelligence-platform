import re
from pathlib import Path

import pandas as pd

# ============================================================
# File Paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

ANALYSIS_FILE = BASE_DIR / "data" / "raw" / "analysis.xlsx"

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

PARSED_OUTPUT = OUTPUT_DIR / "analysis_parsed.csv"
FAILURE_OUTPUT = OUTPUT_DIR / "parse_failures.csv"

# Ratio Engine Output (Update this path if different)
RATIO_FILE = BASE_DIR / "output" / "performance_metrics.csv"

# ============================================================
# Regex Pattern
# ============================================================

PATTERN = re.compile(r"(\d+)\s*Years?:?\s*([\d.]+)%")

# ============================================================
# Columns to Parse
# ============================================================

TARGET_COLUMNS = [
    "compounded_sales_growth",
    "compounded_profit_growth",
    "stock_price_cagr",
    "roe",
]

parsed_rows = []
failed_rows = []

# ============================================================
# Read Excel
# ============================================================

print("Loading analysis.xlsx...")

df = pd.read_excel(ANALYSIS_FILE, header=1)

df.columns = df.columns.str.strip()

print("\nColumns in analysis.xlsx:")
print(df.columns.tolist())
print(df.head())

print(f"Rows Loaded : {len(df)}")

# ============================================================
# Parse Each Column
# ============================================================

for _, row in df.iterrows():

    company = row["company_id"]

    for column in TARGET_COLUMNS:

        value = row.get(column)

        if pd.isna(value):
            continue

        value = str(value)

        match = PATTERN.search(value)

        if match:

            parsed_rows.append(
                {
                    "company_id": company,
                    "metric_type": column,
                    "period_years": int(match.group(1)),
                    "value_pct": float(match.group(2)),
                }
            )

        else:

            failed_rows.append(
                {"company_id": company, "metric_type": column, "original_text": value}
            )

# ============================================================
# Save Parsed CSV
# ============================================================

parsed_df = pd.DataFrame(parsed_rows)

parsed_df.to_csv(PARSED_OUTPUT, index=False)

print(f"Parsed rows : {len(parsed_df)}")

# ============================================================
# Save Failed CSV
# ============================================================

failed_df = pd.DataFrame(failed_rows)

failed_df.to_csv(FAILURE_OUTPUT, index=False)

print(f"Failed rows : {len(failed_df)}")

# ============================================================
# Cross Validation
# ============================================================

"""
try:

    ratio_df = pd.read_csv(RATIO_FILE)

    comparison = parsed_df.merge(
        ratio_df,
        on="company_id",
        how="left"
    )

    divergence = []

    mapping = {
        "compounded_sales_growth": "compounded_sales_growth",
        "compounded_profit_growth": "compounded_profit_growth",
        "stock_price_cagr": "stock_price_cagr",
        "roe": "roe"
    }

    for _, row in comparison.iterrows():

        metric = row["metric_type"]

        if metric not in mapping:
            continue

        ratio_col = mapping[metric]

        if ratio_col not in comparison.columns:
            continue

        calculated = row[ratio_col]

        if pd.isna(calculated):
            continue

        difference = abs(row["value_pct"] - calculated)

        if difference > 5:

            divergence.append({
                "company_id": row["company_id"],
                "metric": metric,
                "parsed_value": row["value_pct"],
                "computed_value": calculated,
                "difference": difference
            })

    divergence_df = pd.DataFrame(divergence)

    divergence_df.to_csv(
        OUTPUT_DIR / "cagr_divergence.csv",
        index=False
    )

    print(f"Divergence Found : {len(divergence_df)}")

except FileNotFoundError:

    print("Ratio Engine output not found. Cross-validation skipped.")

print("Day 29 Parser Completed Successfully!")
"""
