import sqlite3
from pathlib import Path

import pandas as pd
from cashflow_kpis import (
    capital_allocation_pattern,
)

# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "nifty100.db"

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "cashflow_intelligence.xlsx"
DISTRESS_FILE = OUTPUT_DIR / "distress_alerts.csv"


# ==========================================================
# DATABASE
# ==========================================================

conn = sqlite3.connect(DB_PATH)


cashflow = pd.read_sql(
    "SELECT * FROM cashflow",
    conn,
)

ratios = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn,
)

pnl = pd.read_sql(
    "SELECT * FROM profitandloss",
    conn,
)

balancesheet = pd.read_sql(
    "SELECT * FROM balancesheet",
    conn,
)

sectors = pd.read_sql(
    "SELECT * FROM sectors",
    conn,
)


# ==========================================================
# NORMALIZE COLUMN NAMES
# ==========================================================

for data in [
    cashflow,
    ratios,
    pnl,
    balancesheet,
    sectors,
]:

    data.columns = [str(c).strip().lower() for c in data.columns]


# ==========================================================
# HELPER
# ==========================================================


def find_column(df, candidates):

    for column in candidates:

        if column in df.columns:
            return column

    return None


def number(value):

    if pd.isna(value):
        return 0.0

    try:
        return float(value)

    except (TypeError, ValueError):
        return 0.0


# ==========================================================
# FIND REQUIRED COLUMNS
# ==========================================================

sales_col = find_column(
    pnl,
    [
        "sales",
        "revenue",
        "revenue_cr",
        "sales_cr",
        "total_revenue",
    ],
)

operating_profit_col = find_column(
    pnl,
    [
        "operating_profit",
        "operating_profit_cr",
        "op_profit",
    ],
)

net_profit_col = find_column(
    pnl,
    [
        "net_profit",
        "profit_after_tax",
        "pat",
    ],
)

borrowings_col = find_column(
    balancesheet,
    [
        "borrowings",
        "borrowings_cr",
        "total_borrowings",
        "total_debt_cr",
        "total_debt",
    ],
)


# ==========================================================
# MERGE DATA
# ==========================================================

df = cashflow.copy()
# Keep only the official 92-company N100 universe
valid_companies = set(ratios["company_id"].dropna().unique())

df = df[df["company_id"].isin(valid_companies)].copy()

if ratios.shape[1] > 0:

    ratio_columns = [
        "company_id",
        "year",
        "free_cash_flow_cr",
        "cash_from_operations_cr",
        "total_debt_cr",
    ]

    ratio_columns = [c for c in ratio_columns if c in ratios.columns]

    df = df.merge(
        ratios[ratio_columns],
        on=["company_id", "year"],
        how="left",
    )


if net_profit_col:

    pnl_columns = [
        "company_id",
        "year",
        net_profit_col,
    ]

    if sales_col:
        pnl_columns.append(sales_col)

    if operating_profit_col:
        pnl_columns.append(operating_profit_col)

    df = df.merge(
        pnl[pnl_columns],
        on=["company_id", "year"],
        how="left",
    )


if borrowings_col:

    df = df.merge(
        balancesheet[
            [
                "company_id",
                "year",
                borrowings_col,
            ]
        ],
        on=["company_id", "year"],
        how="left",
    )


sector_col = find_column(
    sectors,
    ["broad_sector", "sector"],
)

if sector_col:

    df = df.merge(
        sectors[
            [
                "company_id",
                sector_col,
            ]
        ].drop_duplicates("company_id"),
        on="company_id",
        how="left",
    )

    df.rename(
        columns={sector_col: "sector"},
        inplace=True,
    )

else:

    df["sector"] = "Unknown"


print("Cashflow rows :", len(df))


# ==========================================================
# SORT
# ==========================================================

df = df.sort_values(["company_id", "year"])


# ==========================================================
# CALCULATIONS
# ==========================================================

records = []
distress_records = []


for company_id, company_df in df.groupby("company_id"):

    company_df = company_df.sort_values("year").copy()

    # ------------------------------------------------------
    # FCF
    # ------------------------------------------------------

    company_df["calculated_fcf"] = company_df["operating_activity"].apply(
        number
    ) + company_df["investing_activity"].apply(number)

    # ------------------------------------------------------
    # CFO QUALITY — 5 YEAR AVERAGE
    # ------------------------------------------------------

    recent = company_df.tail(5)

    quality_ratios = []

    for _, row in recent.iterrows():

        pat = number(
            row.get(
                net_profit_col,
                0,
            )
        )

        cfo = number(
            row.get(
                "operating_activity",
                0,
            )
        )

        if pat != 0:

            quality_ratios.append(cfo / pat)

    if quality_ratios:

        avg_quality = sum(quality_ratios) / len(quality_ratios)

        if avg_quality > 1:

            quality_label = "High Quality"

        elif avg_quality >= 0.5:

            quality_label = "Moderate"

        else:

            quality_label = "Accrual Risk"

    else:

        avg_quality = None
        quality_label = "N/A"

    # ------------------------------------------------------
    # LATEST YEAR
    # ------------------------------------------------------

    latest = company_df.iloc[-1]

    latest_cfo = number(
        latest.get(
            "operating_activity",
            0,
        )
    )

    latest_cfi = number(
        latest.get(
            "investing_activity",
            0,
        )
    )

    latest_cff = number(
        latest.get(
            "financing_activity",
            0,
        )
    )

    # ------------------------------------------------------
    # CAPEX INTENSITY
    # ABS(CFI) / SALES
    # ------------------------------------------------------

    latest_sales = number(
        latest.get(
            sales_col,
            0,
        )
    )

    if latest_sales != 0:

        capex_pct = abs(latest_cfi) / latest_sales * 100

        if capex_pct < 3:

            capex_label = "Asset Light"

        elif capex_pct <= 8:

            capex_label = "Moderate"

        else:

            capex_label = "Capital Intensive"

    else:

        capex_pct = None
        capex_label = "N/A"

    # ------------------------------------------------------
    # FCF CAGR — 5 YEAR
    # ------------------------------------------------------

    fcf_series = company_df[["year", "calculated_fcf"]].dropna()

    fcf_cagr = None

    if len(fcf_series) >= 5:

        first_fcf = number(fcf_series.iloc[-5]["calculated_fcf"])

        last_fcf = number(fcf_series.iloc[-1]["calculated_fcf"])

        if first_fcf > 0 and last_fcf > 0:

            fcf_cagr = ((last_fcf / first_fcf) ** (1 / 4) - 1) * 100

    # ------------------------------------------------------
    # FCF CONVERSION
    # FCF / OPERATING PROFIT
    # ------------------------------------------------------

    latest_operating_profit = number(
        latest.get(
            operating_profit_col,
            0,
        )
    )

    latest_fcf = number(latest["calculated_fcf"])

    if latest_operating_profit != 0:

        conversion = latest_fcf / latest_operating_profit * 100

    else:

        conversion = None

    # ------------------------------------------------------
    # DISTRESS SIGNAL
    # CFO < 0 AND CFF > 0
    # ------------------------------------------------------

    distress_flag = latest_cfo < 0 and latest_cff > 0

    if distress_flag:

        distress_records.append(
            {
                "company_id": company_id,
                "cfo": latest_cfo,
                "cff": latest_cff,
                "net_profit": number(
                    latest.get(
                        net_profit_col,
                        0,
                    )
                ),
            }
        )

    # ------------------------------------------------------
    # DELEVERAGING
    # CFF < 0 AND BORROWINGS DECLINING YOY
    # ------------------------------------------------------

    deleveraging = False

    if borrowings_col and len(company_df) >= 2:

        previous = company_df.iloc[-2]

        previous_borrowings = number(
            previous.get(
                borrowings_col,
                0,
            )
        )

        latest_borrowings = number(
            latest.get(
                borrowings_col,
                0,
            )
        )

        deleveraging = latest_cff < 0 and latest_borrowings < previous_borrowings

    # ------------------------------------------------------
    # CAPITAL ALLOCATION
    # ------------------------------------------------------

    allocation = capital_allocation_pattern(
        latest_cfo,
        latest_cfi,
        latest_cff,
    )

    # ------------------------------------------------------
    # RECORD
    # ------------------------------------------------------

    records.append(
        {
            "company_id": company_id,
            "sector": latest.get(
                "sector",
                "Unknown",
            ),
            "cfo_quality_score": avg_quality,
            "cfo_quality_label": quality_label,
            "capex_intensity_pct": capex_pct,
            "capex_label": capex_label,
            "fcf_cagr_5yr": fcf_cagr,
            "fcf_conversion_pct": conversion,
            "distress_flag": distress_flag,
            "deleveraging_flag": deleveraging,
            "capital_allocation_label": allocation,
        }
    )


# ==========================================================
# SAVE OUTPUT
# ==========================================================

cashflow_df = pd.DataFrame(records)

cashflow_df = cashflow_df.sort_values("company_id")

cashflow_df.to_excel(
    OUTPUT_FILE,
    index=False,
)


distress_df = pd.DataFrame(distress_records)

distress_df.to_csv(
    DISTRESS_FILE,
    index=False,
)


# ==========================================================
# SUMMARY
# ==========================================================

print()
print("=" * 60)
print("DAY 31 CASH FLOW INTELLIGENCE")
print("=" * 60)

print()

print(
    "Companies :",
    cashflow_df["company_id"].nunique(),
)

print(
    "Rows :",
    len(cashflow_df),
)

print(
    "Distress Companies :",
    len(distress_df),
)

print()

print(cashflow_df.head(20))

print()

print(
    "Generated:",
    OUTPUT_FILE,
)

print(
    "Generated:",
    DISTRESS_FILE,
)


conn.close()
