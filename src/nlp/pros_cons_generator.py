import sqlite3
from pathlib import Path

import pandas as pd


# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "nifty100.db"

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "pros_cons_generated.csv"


# ==========================================================
# CONNECT DATABASE
# ==========================================================

conn = sqlite3.connect(DB_PATH)

query = """
SELECT
    fr.company_id,
    fr.year,

    fr.return_on_equity_pct,
    fr.debt_to_equity,
    fr.interest_coverage,
    fr.operating_profit_margin_pct,
    fr.free_cash_flow_cr,
    fr.earnings_per_share,
    fr.dividend_payout_ratio_pct,
    fr.total_debt_cr,

    a.compounded_sales_growth,
    a.compounded_profit_growth,
    a.stock_price_cagr,
    a.roe,

    mc.pe_ratio,
    mc.pb_ratio,
    mc.dividend_yield_pct,

    c.company_name

FROM financial_ratios fr

LEFT JOIN analysis a
ON fr.company_id = a.company_id

LEFT JOIN market_cap mc
ON fr.company_id = mc.company_id

LEFT JOIN companies c
ON fr.company_id = c.id
"""

df = pd.read_sql(query, conn)

# Official 92-company universe
valid_companies = set(
    pd.read_sql(
        "SELECT DISTINCT company_id FROM financial_ratios",
        conn
    )["company_id"]
)

df = df[
    df["company_id"].isin(valid_companies)
].copy()

print(df.head())
print("Rows :", len(df))


# ==========================================================
# HELPERS
# ==========================================================

def safe_float(value):

    if pd.isna(value):
        return None

    try:
        return float(
            str(value)
            .split(":")[-1]
            .replace("%", "")
            .replace(",", "")
            .strip()
        )
    except:
        return None


def add_pro(company, rule_id, text, confidence):

    if confidence >= 60:

        pros_cons.append({
            "company_id": company,
            "type": "pro",
            "rule_id": rule_id,
            "text": text,
            "confidence_pct": confidence
        })


def add_con(company, rule_id, text, confidence):

    if confidence >= 60:

        pros_cons.append({
            "company_id": company,
            "type": "con",
            "rule_id": rule_id,
            "text": text,
            "confidence_pct": confidence
        })


# ==========================================================
# GENERATE PROS & CONS
# ==========================================================

pros_cons = []


for _, row in df.iterrows():

    company = row["company_id"]


    # ======================================================
    # PRO RULES
    # ======================================================

    # PRO1
    if row["return_on_equity_pct"] > 20:

        add_pro(
            company,
            "PRO1",
            "Consistently high return on equity above 20% demonstrates exceptional capital efficiency.",
            90
        )


    # PRO2
    if row["free_cash_flow_cr"] > 0:

        add_pro(
            company,
            "PRO2",
            "Strong free cash flow generation signals healthy business fundamentals.",
            85
        )


    # PRO3
    if row["debt_to_equity"] == 0:

        add_pro(
            company,
            "PRO3",
            "Debt-free balance sheet provides financial flexibility.",
            95
        )


    # PRO4
    if row["operating_profit_margin_pct"] > 25:

        add_pro(
            company,
            "PRO4",
            "Operating profit margin above 25% indicates strong pricing power.",
            85
        )


    # PRO5
    if row["interest_coverage"] > 10:

        add_pro(
            company,
            "PRO5",
            "Very high interest coverage reflects negligible financial stress.",
            80
        )


    # PRO6
    profit_growth = safe_float(
        row["compounded_profit_growth"]
    )

    if profit_growth is not None and profit_growth > 20:

        add_pro(
            company,
            "PRO6",
            "Net profit compounding above 20% creates significant shareholder value.",
            88
        )


    # PRO7
    if (
        row["interest_coverage"] > 10
        or
        row["debt_to_equity"] == 0
    ):

        add_pro(
            company,
            "PRO7",
            "Strong balance-sheet quality reduces financial stress.",
            82
        )


    # PRO8
    dividend_yield = safe_float(
        row["dividend_yield_pct"]
    )

    if (
        dividend_yield is not None
        and dividend_yield > 2
        and row["free_cash_flow_cr"] > 0
    ):

        add_pro(
            company,
            "PRO8",
            "Dividend yield above 2% backed by positive free cash flow.",
            84
        )


    # PRO9
    if row["earnings_per_share"] > 50:

        add_pro(
            company,
            "PRO9",
            "Strong earnings per share indicates healthy earnings quality.",
            80
        )


    # PRO10
    if row["return_on_equity_pct"] > 15:

        add_pro(
            company,
            "PRO10",
            "Return on equity indicates strengthening business quality.",
            78
        )


    # PRO11
    sales_growth = safe_float(
        row["compounded_sales_growth"]
    )

    if (
        profit_growth is not None
        and sales_growth is not None
        and profit_growth > sales_growth
    ):

        add_pro(
            company,
            "PRO11",
            "Profits are compounding faster than revenue, indicating operating leverage.",
            83
        )


    # PRO12
    if row["debt_to_equity"] < 0.5:

        add_pro(
            company,
            "PRO12",
            "Low leverage supports long-term sustainable growth.",
            80
        )


    # ======================================================
    # CON RULES
    # ======================================================

    # CON1
    if row["debt_to_equity"] > 2:

        add_con(
            company,
            "CON1",
            f"Debt-to-equity ratio of {row['debt_to_equity']:.2f} is elevated.",
            90
        )


    # CON2
    if row["free_cash_flow_cr"] < 0:

        add_con(
            company,
            "CON2",
            "Negative free cash flow raises concern about cash generation.",
            80
        )


    # CON3
    if row["interest_coverage"] < 1.5:

        add_con(
            company,
            "CON3",
            "Interest coverage below 1.5x indicates debt servicing risk.",
            85
        )


    # CON4
    if row["operating_profit_margin_pct"] < 10:

        add_con(
            company,
            "CON4",
            "Operating margin is relatively weak.",
            75
        )


    # CON5
    if row["return_on_equity_pct"] < 10:

        add_con(
            company,
            "CON5",
            "Low return on equity indicates poor capital efficiency.",
            80
        )


    # CON6
    if row["interest_coverage"] < 1.5:

        add_con(
            company,
            "CON6",
            "Low interest coverage increases financial risk.",
            90
        )


    # CON7
    if row["dividend_payout_ratio_pct"] > 100:

        add_con(
            company,
            "CON7",
            "Dividend payout above 100% appears unsustainable.",
            88
        )


    # CON8
    if row["debt_to_equity"] > 1.5:

        add_con(
            company,
            "CON8",
            "Debt levels are relatively high.",
            82
        )


    # CON9
    if row["earnings_per_share"] < 5:

        add_con(
            company,
            "CON9",
            "Low earnings per share indicates weak profitability.",
            75
        )


    # CON10
    if row["return_on_equity_pct"] < 10:

        add_con(
            company,
            "CON10",
            "Low return on capital efficiency.",
            82
        )


    # CON11
    if row["total_debt_cr"] > 1000:

        add_con(
            company,
            "CON11",
            "High debt limits financial flexibility.",
            78
        )


    # CON12
    if (
        sales_growth is not None
        and sales_growth < 5
    ):

        add_con(
            company,
            "CON12",
            "Revenue growth below 5% suggests limited business momentum.",
            85
        )


# ==========================================================
# CREATE DATAFRAME
# ==========================================================

pros_cons_df = pd.DataFrame(
    pros_cons
)


# ==========================================================
# REMOVE DUPLICATES
# ==========================================================

pros_cons_df.drop_duplicates(
    subset=[
        "company_id",
        "rule_id",
        "type"
    ],
    inplace=True
)


# ==========================================================
# ENSURE EVERY COMPANY HAS PRO + CON
# ==========================================================

all_companies = df[
    "company_id"
].drop_duplicates()


for company in all_companies:

    company_rows = pros_cons_df[
        pros_cons_df["company_id"] == company
    ]



# ==========================================================
# SORT
# ==========================================================

pros_cons_df = pros_cons_df.sort_values(
    by=[
        "company_id",
        "type",
        "rule_id"
    ]
)

pros_cons_df.reset_index(
    drop=True,
    inplace=True
)


# ==========================================================
# SAVE
# ==========================================================

pros_cons_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ==========================================================
# SUMMARY
# ==========================================================

print()

print("=" * 60)
print("DAY 30 COMPLETED")
print("=" * 60)

print()

print(
    "Companies :",
    pros_cons_df["company_id"].nunique()
)

print(
    "Total Records :",
    len(pros_cons_df)
)

print(
    "Total Rules :",
    pros_cons_df["rule_id"].nunique()
)

print(
    "Pro Rules :",
    pros_cons_df[
        pros_cons_df["type"] == "pro"
    ]["rule_id"].nunique()
)

print(
    "Con Rules :",
    pros_cons_df[
        pros_cons_df["type"] == "con"
    ]["rule_id"].nunique()
)

print()

print(
    pros_cons_df.head(20)
)


conn.close()