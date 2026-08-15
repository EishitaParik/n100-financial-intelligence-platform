import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "nifty100.db"
OUTPUT = ROOT / "output"

OUTPUT.mkdir(exist_ok=True)


# ============================================================
# LOAD LATEST DATA
# ============================================================

conn = sqlite3.connect(DB)

df = pd.read_sql_query(
    """
    SELECT
        fr.company_id,
        fr.year,
        fr.return_on_equity_pct,
        fr.debt_to_equity,
        fr.operating_profit_margin_pct,
        fr.free_cash_flow_cr,
        s.broad_sector
    FROM financial_ratios fr
    LEFT JOIN sectors s
        ON fr.company_id = s.company_id
    WHERE fr.year = (
        SELECT MAX(fr2.year)
        FROM financial_ratios fr2
        WHERE fr2.company_id = fr.company_id
    )
    """,
    conn,
)

conn.close()


# ============================================================
# METRICS
# ============================================================

metrics = [
    "return_on_equity_pct",
    "debt_to_equity",
    "operating_profit_margin_pct",
    "free_cash_flow_cr",
]


for metric in metrics:
    df[metric] = pd.to_numeric(
        df[metric],
        errors="coerce",
    )


# ============================================================
# OUTLIERS — Z SCORE WITHIN SECTOR
# ============================================================

outliers = []

for sector, group in df.groupby("broad_sector"):

    for metric in metrics:

        values = group[metric]

        mean = values.mean()
        std = values.std()

        if pd.isna(std) or std == 0:
            continue

        z_scores = (values - mean) / std

        for index in group.index:

            z = z_scores.loc[index]

            if abs(z) > 3:

                outliers.append(
                    {
                        "company_id": df.loc[index, "company_id"],
                        "sector": sector,
                        "metric": metric,
                        "value": df.loc[index, metric],
                        "z_score": z,
                    }
                )


outlier_df = pd.DataFrame(outliers)

outlier_path = OUTPUT / "outlier_report.csv"

outlier_df.to_csv(
    outlier_path,
    index=False,
)


# ============================================================
# PORTFOLIO STATISTICS
# ============================================================

portfolio_metrics = [
    "return_on_equity_pct",
    "debt_to_equity",
    "operating_profit_margin_pct",
    "free_cash_flow_cr",
]


rows = []

for metric in portfolio_metrics:

    values = df[metric].dropna()

    rows.append(
        {
            "metric": metric,
            "P10": np.percentile(values, 10),
            "P25": np.percentile(values, 25),
            "P50": np.percentile(values, 50),
            "P75": np.percentile(values, 75),
            "P90": np.percentile(values, 90),
            "Mean": values.mean(),
            "Std": values.std(),
        }
    )


portfolio_df = pd.DataFrame(rows)

portfolio_path = OUTPUT / "portfolio_stats.csv"

portfolio_df.to_csv(
    portfolio_path,
    index=False,
)


# ============================================================
# OUTPUT
# ============================================================

print("=" * 70)
print("DAY 37 COMPLETE")
print("=" * 70)

print(f"\nCompanies analysed: " f"{df['company_id'].nunique()}")

print(f"\nOutliers found: " f"{len(outlier_df)}")

print(f"\nCreated:" f"\n{outlier_path}" f"\n{portfolio_path}")

print("\nPortfolio statistics:")
print(portfolio_df.round(2).to_string(index=False))
